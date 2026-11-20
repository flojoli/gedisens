# Figures

Final figures of the analysis, created from the full Kalkalpen dataset
(see [data/README.md](../data/README.md)). Only final figures belong
here, not test runs.

> PNG files in this folder are **not** committed yet (see `.gitignore`):
> they show ALS data whose licence still has to be clarified. Once it is,
> remove the `figures/*.png` line from `.gitignore`.

| File | Command |
| --- | --- |
| `GEDIamp_vs_ALSpulse_35070600200401943.png` | `gedisens --data-file GEDI.shp --structure-plot --shot-number 35070600200401943 --add-info fhd --out-dir figures` |
| `correlation_plot_gediFHDcal_vs_alsFHD.png` | `gedisens --data-file GEDI.shp --correlation-plot --x-var alsFHD --y-var gediFHDcal --out-dir figures` |
| `boxplot.png` | `gedisens --data-file GEDI.shp --boxplot --group StrucALS --group-var gediFHDcal --out-dir figures` |

`GEDI.shp` is `Kalkalpen/masterfile/GEDI.shp`. All figures: gedisens 0.2.0.
