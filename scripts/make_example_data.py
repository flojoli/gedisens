"""Creates the example dataset data/example/gedisens_example.gpkg.

GEDI columns are real (NASA GEDI, open data). All ALS columns are
SYNTHETIC: they are derived from the GEDI waveform plus random noise so
that every gedisens command can be tried without the restricted ALS data.

Usage:

    poetry run python scripts/make_example_data.py <path to GEDI.shp>

"""

import sys
from pathlib import Path

import numpy as np

from gedisens import io, profiles, structure

N_PER_CLASS = 10
DEMO_SHOT = "35070600200401943"
SEED = 42
OUT = (
    Path(__file__).resolve().parents[1] / "data/example/gedisens_example.gpkg"
)

GEDI_COLS = [
    "Shot_Numbe",
    "Latitude",
    "Longitude",
    "RH_90",
    "gediFHDl2b",
    "gediFHDcal",
    "NoL_GEDI",
    "StrucGEDI",
]


def select_footprints(data, rng):
    """Selects the demo shot and a few footprints per GEDI structure class.

    Args:

        data (geopandas dataframe): full master file.

        rng (numpy generator): random generator.

    Returns: geopandas dataframe with the selected footprints.

    """
    candidates = data[(data.StrucGEDI > 0) & (data.gediFHDcal > 0)]
    picks = [data[data.Shot_Numbe == DEMO_SHOT]]
    for cls in (1, 2, 3):
        group = candidates[
            (candidates.StrucGEDI == cls)
            & (candidates.Shot_Numbe != DEMO_SHOT)
        ]
        idx = rng.choice(len(group), size=N_PER_CLASS, replace=False)
        picks.append(group.iloc[np.sort(idx)])
    return data.loc[[i for p in picks for i in p.index]]


def synthetic_als(gdf, rng):
    """Adds synthetic ALS columns derived from the GEDI waveform.

    Pulse values are the GEDI amplitude share in % with multiplicative
    noise, rounded to integers like the original ALS returns.

    Args:

        gdf (geopandas dataframe): footprints with Amp columns.

        rng (numpy generator): random generator.

    Returns: geopandas dataframe with Pulse, alsFHD, alsFHDco, NoL_ALS
             and StrucALS columns added.

    """
    amp_cols = profiles.profile_columns(gdf, "Amp")
    amp = gdf[amp_cols].to_numpy(float).clip(min=0)
    share = amp / amp.sum(axis=1, keepdims=True) * 100
    noisy = share * rng.lognormal(0, 0.4, size=share.shape)
    pulse = np.round(noisy / noisy.sum(axis=1, keepdims=True) * 100)

    gdf = gdf.copy()
    for col, values in zip(amp_cols, pulse.T, strict=True):
        gdf[col.replace("Amp", "Pulse")] = values

    fhd = structure.calc_fhd(gdf, "Pulse").fhd
    gdf["alsFHD"] = fhd
    gdf["alsFHDco"] = fhd

    layers = profiles.get_max_height(gdf).apply(
        lambda row: structure.calc_layers(
            structure.calc_upper_percentage(row)
        ),
        axis=1,
    )
    gdf["NoL_ALS"] = layers.NoL

    flip = rng.random(len(gdf)) < 0.2
    gdf["StrucALS"] = np.where(
        flip, rng.integers(1, 4, len(gdf)), gdf.StrucGEDI
    )
    return gdf


def main(master_file):
    """Builds and writes the example dataset.

    Args:

        master_file (str): path to the Kalkalpen master file GEDI.shp.

    """
    rng = np.random.default_rng(SEED)
    data = io.read_vector(master_file)
    amp_cols = profiles.profile_columns(data, "Amp")

    example = select_footprints(data, rng)
    example = example[GEDI_COLS + amp_cols + ["geometry"]]
    example = synthetic_als(example, rng)

    path = io.write_vector(example.reset_index(drop=True), OUT)
    print(f"{len(example)} footprints written to {path}")


if __name__ == "__main__":
    main(sys.argv[1])
