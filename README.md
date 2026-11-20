# gedisens

Tools to assess vertical forest structure from airborne laser scanning
(ALS) and spaceborne GEDI LiDAR data, and to compare the two.

`gedisens` works on vector files (shapefile, GeoPackage, ...) in which each
row is one GEDI footprint and the vertical profiles are stored as one column
per 1 m height bin:

| Column pattern | Content |
| --- | --- |
| `Shot_Numbe` | GEDI shot number |
| `Amp<i>_<i+1>` | GEDI waveform amplitude between *i* and *i+1* m |
| `Pulse<i>_<i+1>` | ALS returns between *i* and *i+1* m |
| `RH_90` | GEDI relative height 90 (used as canopy height for layers) |
| `gediFHDl2b`, `gediFHDcal`, `alsFHD`, `alsFHDco` | FHD values (for plots) |
| `NoL_GEDI`, `NoL_ALS` | number of layers (for plots) |
| `StrucGEDI`, `StrucALS` | interpreted structure class 1–3 (for boxplots) |

## Features

- **Foliage height diversity (FHD)**: Shannon index of the GEDI or ALS
  profile (ground bin excluded).
- **Number of layers (NoL)**: threshold-based layer detection using the
  share of the profile in the upper sixth of the canopy.
- **Plots**: GEDI vs. ALS profile of a footprint, correlation with OLS fit,
  and boxplots per structure class.

## Installation

Requires Python ≥ 3.11 and [Poetry](https://python-poetry.org/) ≥ 2.0.

```bash
git clone git@gitlab.com:flojoli/gedisens.git
cd gedisens
poetry install
```

Alternatively, with plain pip:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

## Example data

[`data/example/`](data/example/) contains 31 footprints to try every
command right away. Its GEDI values are real; **its ALS values are
synthetic** (see [data/README.md](data/README.md)). The full analysis data
is not part of this repository. Final figures go into
[`figures/`](figures/README.md).

```bash
gedisens --data-file data/example/gedisens_example.gpkg --structure-plot \
         --shot-number 35070600200401943 --add-info fhd
```

## Usage

Run `gedisens --help` for all options. Results are written to `--out-dir`;
without it, plots are shown in a window. Tables are written as GeoPackage
(`<input name>_fhd.gpkg`, `<input name>_layers.gpkg`) so long column names
are kept.

Structure plot of one footprint (`--add-info`: `fhd`, `numb_lay` or
`stdv_var`):

```bash
gedisens --data-file GEDI.shp --structure-plot --shot-number 35070600200401943 \
         --add-info fhd --out-dir output
```

Correlation plot:

```bash
gedisens --data-file GEDI.shp --correlation-plot --x-var alsFHD --y-var gediFHDcal \
         --out-dir output
```

Boxplot per structure class:

```bash
gedisens --data-file GEDI.shp --boxplot --group StrucALS --group-var gediFHDcal \
         --out-dir output
```

FHD and number of layers from ALS (`Pulse`, default) or GEDI (`Amp`)
profiles:

```bash
gedisens --data-file GEDI.shp --fhd --layers --attribute-name Amp --out-dir output
```

The old single-dash options (`-data-file`, `-fhd`, ...) still work.

### Python API

```python
from gedisens import io, structure

data = io.read_vector("GEDI.shp")
data = structure.calc_fhd(data, "Amp")
```

## Development

```bash
poetry install                # includes pytest and ruff
poetry run pytest             # run tests
poetry run ruff check .       # lint
poetry run ruff format .      # format
```

Set `GEDISENS_TEST_DATA` to the Kalkalpen master file to also check that the
FHD calculation reproduces the stored `gediFHDcal` and `alsFHDco` values:

```bash
GEDISENS_TEST_DATA=/path/to/GEDI.shp poetry run pytest
```

## License

MIT, see [LICENSE](LICENSE).
