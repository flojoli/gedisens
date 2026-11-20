import math
import os
from pathlib import Path

import geopandas as gpd
import matplotlib
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import Point

from gedisens import io, profiles, stats, structure
from gedisens.cli import gedisens

matplotlib.use("Agg")

N_BINS = 50


def make_profile_df(profiles, prefix):
    """Build a frame with ``<prefix>i_i+1`` columns from a list of dicts."""
    rows = []
    for profile in profiles:
        row = {f"{prefix}{i}_{i + 1}": 0.0 for i in range(N_BINS)}
        row.update({f"{prefix}{i}_{i + 1}": v for i, v in profile.items()})
        rows.append(row)
    return pd.DataFrame(rows)


@pytest.fixture
def sample_gdf():
    amp = make_profile_df([{5: 1, 20: 2, 25: 1}, {}, {10: 1}], "Amp")
    pulse = make_profile_df([{0: 5, 5: 1, 20: 2}, {}, {10: 1}], "Pulse")
    df = pd.concat([amp, pulse], axis=1)
    df.insert(0, "Shot_Numbe", ["1", "2", "3"])
    df["RH_90"] = [24.6, 0.0, 10.2]
    df["gediFHDcal"] = [1.04, 0.0, 0.0]
    df["gediFHDl2b"] = [1.1, 0.0, 0.0]
    df["alsFHD"] = [0.9, 0.0, 0.0]
    df["alsFHDco"] = [0.64, 0.0, 0.0]
    df["NoL_GEDI"] = [2.0, np.nan, 1.0]
    df["NoL_ALS"] = [2.0, np.nan, 1.0]
    df["StrucALS"] = [1, 0, 2]
    geom = [Point(14.4, 47.7 + i * 0.001) for i in range(len(df))]
    return gpd.GeoDataFrame(df, geometry=geom, crs="EPSG:4326")


def test_profile_columns_sorted_numerically():
    df = pd.DataFrame(columns=["Amp10_11", "Amp2_3", "Amp0_1", "Other"])
    assert profiles.profile_columns(df, "Amp") == [
        "Amp0_1",
        "Amp2_3",
        "Amp10_11",
    ]


def test_fhd_uniform_profile_is_log_n():
    df = make_profile_df([{1: 1, 2: 1, 3: 1, 4: 1}], "Amp")
    assert structure.calc_fhd(df, "Amp").fhd.iloc[0] == round(math.log(4), 2)


def test_fhd_ignores_ground_and_handles_empty():
    df = make_profile_df([{0: 100, 5: 1}, {}], "Pulse")
    fhd = structure.calc_fhd(df, "Pulse").fhd
    assert fhd.iloc[0] == 0.0
    assert np.isnan(fhd.iloc[1])


def test_fhd_missing_prefix_raises():
    with pytest.raises(KeyError):
        structure.calc_fhd(pd.DataFrame({"a": [1]}), "Amp")


def _layers(profile, height):
    df = make_profile_df([profile], "Pulse")
    df["RH_90"] = height
    row = profiles.get_max_height(df).iloc[0]
    return structure.calc_layers(structure.calc_upper_percentage(row))


def test_single_layer_when_energy_in_upper_sixth():
    row = _layers({27: 10, 28: 10, 29: 10, 5: 1}, 30)
    assert row.upper_percentage > 0.5
    assert row.NoL == 1


def test_multi_layer_when_little_energy_in_upper_sixth():
    row = _layers({i: 1 for i in range(1, 30)}, 30)
    assert row.upper_percentage < 0.3
    assert row.NoL == 3


def test_two_layers_with_distinct_lower_layer():
    row = _layers({25: 4, 26: 4, 27: 4, 5: 7, 6: 7}, 30)
    assert 0.3 <= row.upper_percentage < 0.5
    assert row.NoL == 2


def test_empty_profile_gives_nan():
    row = _layers({}, 20)
    assert np.isnan(row.upper_percentage)
    assert np.isnan(row.NoL)


def test_height_above_profile_range_does_not_crash():
    row = _layers({45: 1, 49: 1}, 80)
    assert not np.isnan(row.NoL)


def test_vector_preparation_trims_empty_top_bins():
    df = pd.DataFrame({"Shot_Numbe": ["1"], "A": [1.0], "B": [2.0], "C": [0]})
    assert profiles.vector_preparation(df) == [(1, 1.0), (2, 2.0)]


def test_stats_on_histogram():
    s = stats.Stats([(1, 1), (3, 1)])
    assert (s.mean, s.variance, s.stdv) == (2, 1, 1)
    assert math.isnan(stats.Stats([(1, 0)]).mean)


def test_ols_regression_perfect_fit():
    df = pd.DataFrame({"x": [0, 1, 2, 3], "y": [5, 2, 4, 6]})
    out, model, _, r2, _, rmse = stats.ols_regression(df, "y", "x")
    assert len(out) == 3  # zero x dropped
    assert r2 == 1.0 and rmse == 0.0
    assert model.params.iloc[1] == pytest.approx(2)


def test_group_data_drops_zero_groups(sample_gdf):
    groups = stats.group_data(sample_gdf, "StrucALS", "gediFHDcal")
    assert [len(g) for g in groups] == [1]


def test_vector_roundtrip(tmp_path, sample_gdf):
    path = io.write_vector(sample_gdf, tmp_path / "out")
    assert path.suffix == ".gpkg"
    back = io.read_vector(path)
    assert back.Shot_Numbe.tolist() == ["1", "2", "3"]
    assert back.crs == sample_gdf.crs


def test_cli_end_to_end(tmp_path, sample_gdf):
    data = tmp_path / "data.gpkg"
    sample_gdf.to_file(data)
    out = tmp_path / "out"
    gedisens(
        [
            "--data-file",
            str(data),
            "--out-dir",
            str(out),
            "--fhd",
            "--layers",
            "--attribute-name",
            "Amp",
            "--structure-plot",
            "--shot-number",
            "1",
            "--add-info",
            "fhd",
        ]
    )
    fhd = gpd.read_file(out / "data_fhd.gpkg")
    assert fhd.fhd_Amp.iloc[0] == pytest.approx(1.04)
    layers = gpd.read_file(out / "data_layers.gpkg")
    assert "NoL_Amp" in layers.columns
    assert (out / "GEDIamp_vs_ALSpulse_1.png").exists()


def test_cli_accepts_legacy_single_dash(tmp_path, sample_gdf):
    data = tmp_path / "data.gpkg"
    sample_gdf.to_file(data)
    gedisens(
        [
            "-data-file",
            str(data),
            "-structure-plot",
            "-shot-number",
            "1",
            "-add-info",
            "numb_lay",
            "-out-dir",
            str(tmp_path),
        ]
    )
    assert (tmp_path / "GEDIamp_vs_ALSpulse_1.png").exists()


def test_cli_requires_options(tmp_path):
    with pytest.raises(SystemExit):
        gedisens(["--data-file", "x.shp", "--correlation-plot"])


EXAMPLE = (
    Path(__file__).resolve().parents[1] / "data/example/gedisens_example.gpkg"
)


def test_example_data_runs_all_commands(tmp_path):
    base = ["--data-file", str(EXAMPLE), "--out-dir", str(tmp_path)]
    gedisens(
        base
        + [
            "--structure-plot",
            "--shot-number",
            "35070600200401943",
            "--add-info",
            "fhd",
        ]
    )
    gedisens(
        base
        + ["--correlation-plot", "--x-var", "alsFHD", "--y-var", "gediFHDcal"]
    )
    gedisens(
        base
        + ["--boxplot", "--group", "StrucALS", "--group-var", "gediFHDcal"]
    )
    gedisens(base + ["--fhd", "--layers", "--attribute-name", "Amp"])
    assert len(list(tmp_path.glob("*.png"))) == 3
    assert len(list(tmp_path.glob("*.gpkg"))) == 2


def test_example_gedi_fhd_matches_stored_values():
    data = io.read_vector(EXAMPLE)
    fhd = structure.calc_fhd(data, "Amp").fhd
    np.testing.assert_allclose(fhd, data.gediFHDcal, atol=0.011)


REAL_DATA = os.environ.get("GEDISENS_TEST_DATA")


@pytest.mark.skipif(not REAL_DATA, reason="set GEDISENS_TEST_DATA")
def test_fhd_reproduces_stored_values():
    """FHD reproduces gediFHDcal (Amp) and alsFHDco (Pulse) of the
    Kalkalpen master file."""
    data = io.read_vector(REAL_DATA)
    for prefix, ref in [("Amp", "gediFHDcal"), ("Pulse", "alsFHDco")]:
        fhd = structure.calc_fhd(data, prefix).fhd.fillna(0)
        mask = data[ref] > 0
        np.testing.assert_allclose(fhd[mask], data[ref][mask], atol=0.011)
