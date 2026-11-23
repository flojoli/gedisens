# Data

## Example data (`example/gedisens_example.gpkg`)

A small dataset to try all `gedisens` commands right after cloning:

```bash
gedisens --data-file data/example/gedisens_example.gpkg --structure-plot \
         --shot-number 35070600200401943 --add-info fhd
```

- 31 GEDI footprints from the Kalkalpen National Park study area
  (Upper Austria): shot `35070600200401943` (used in the README examples)
  plus 10 randomly chosen footprints per GEDI structure class.
- GeoPackage, EPSG:4326, one row per footprint.
> **The ALS columns are synthetic.** They are the GEDI waveform share in %
> multiplied by random log-normal noise (σ = 0.4, seed 42) and rounded,
> and are only meant for trying the code.
> Do **not** use them for any analysis. All GEDI columns are real.

| Column | Source | Content |
| --- | --- | --- |
| `Shot_Numbe` | GEDI | shot number |
| `Latitude`, `Longitude` | GEDI | footprint centre |
| `RH_90` | GEDI L2A | relative height 90 % [m] |
| `Amp<i>_<i+1>` | GEDI | waveform amplitude between *i* and *i+1* m |
| `gediFHDl2b` | GEDI L2B | foliage height diversity from the L2B product |
| `gediFHDcal` | GEDI | FHD calculated from `Amp*` with gedisens |
| `NoL_GEDI` | GEDI | number of layers (interpretation) |
| `StrucGEDI` | GEDI | structure class 1 = low, 2 = medium, 3 = high (interpretation) |
| `Pulse<i>_<i+1>` | **synthetic** | ALS returns between *i* and *i+1* m [%] |
| `alsFHD`, `alsFHDco` | **synthetic** | FHD calculated from `Pulse*` |
| `NoL_ALS` | **synthetic** | number of layers calculated from `Pulse*` |
| `StrucALS` | **synthetic** | structure class (80 % = `StrucGEDI`, 20 % random) |

## Full analysis data

The full dataset is not part of this repository.

| | |
| --- | --- |
| File | `Kalkalpen/masterfile/GEDI.shp` (9,065 footprints, 161 columns, EPSG:4326) |
| Archive | TODO: Zenodo DOI once published |
| GEDI | NASA GEDI L2A/L2B, open data via [LP DAAC](https://lpdaac.usgs.gov/) / [ORNL DAAC](https://daac.ornl.gov/) |
| ALS | TODO: provider, acquisition year and licence (e.g. Nationalpark Kalkalpen / Land Oberösterreich) |
| Interpretations | TODO: who interpreted `StrucGEDI`/`StrucALS`/`NoL_*` and how |
