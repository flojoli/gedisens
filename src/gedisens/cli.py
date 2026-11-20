"""Command line interface of gedisens."""

import argparse
import logging
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from gedisens import io, plots, profiles, stats, structure

GROUP_VARS = ["gediFHDcal", "gediFHDl2b", "alsFHD", "alsFHDco"]


def _version():
    """Returns the installed version of gedisens.

    Returns: version string, unknown if the package is not installed.

    """
    try:
        return version("gedisens")
    except PackageNotFoundError:
        return "unknown"


def _add(parser, name, **kwargs):
    """Adds an option as --name and as the old single-dash -name.

    Args:

        parser (argparse parser or group): where the option is added.

        name (str): option name without dashes, e.g. data-file.

        **kwargs: passed to add_argument.

    """
    parser.add_argument(f"--{name}", f"-{name}", **kwargs)


def build_parser():
    """Builds the command line parser.

    Returns: argparse parser with all gedisens options.

    """
    parser = argparse.ArgumentParser(
        prog="gedisens",
        description=(
            "Compare vertical forest structure from ALS and GEDI LiDAR data."
        ),
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {_version()}"
    )
    _add(
        parser,
        "data-file",
        dest="data_file",
        required=True,
        help="Input vector file (shapefile, GeoPackage, ...).",
    )
    _add(
        parser,
        "out-dir",
        dest="output_dir",
        default="",
        help="Output directory. Plots are shown instead if omitted.",
    )
    _add(
        parser,
        "verbose",
        dest="verbose",
        action="store_true",
        help="Print progress information.",
    )

    calcs = parser.add_argument_group("calculations")
    _add(
        calcs,
        "layers",
        dest="layers",
        action="store_true",
        help="Calculate the number of layers (NoL) per footprint.",
    )
    _add(
        calcs,
        "fhd",
        dest="fhd",
        action="store_true",
        help="Calculate foliage height diversity (FHD).",
    )
    _add(
        calcs,
        "attribute-name",
        dest="attr_name",
        default="Pulse",
        choices=["Pulse", "Amp"],
        help="Profile used for --layers/--fhd: ALS 'Pulse' (default) "
        "or GEDI 'Amp'.",
    )
    _add(
        calcs,
        "height-col",
        dest="height_col",
        default="RH_90",
        help="Canopy height column for --layers (default: RH_90).",
    )

    struct = parser.add_argument_group("structure plot")
    _add(
        struct,
        "structure-plot",
        dest="structure_plot",
        action="store_true",
        help="Plot ALS and GEDI profiles of a shot.",
    )
    _add(
        struct, "shot-number", dest="shot_number", help="Shot number to plot."
    )
    _add(
        struct,
        "dz",
        dest="dz",
        type=int,
        default=1,
        help="Vertical bin size in m (default: 1).",
    )
    _add(
        struct,
        "add-info",
        dest="add_info",
        default="",
        choices=["fhd", "stdv_var", "numb_lay"],
        help="Additional info shown in the plot.",
    )

    corr = parser.add_argument_group("correlation plot")
    _add(
        corr,
        "correlation-plot",
        dest="correlation_plot",
        action="store_true",
        help="Plot correlation with OLS fit.",
    )
    _add(corr, "x-var", dest="x_var", help="x (ALS) variable.")
    _add(corr, "y-var", dest="y_var", help="y (GEDI) variable.")

    box = parser.add_argument_group("boxplot")
    _add(
        box,
        "boxplot",
        dest="boxplot",
        action="store_true",
        help="Boxplot of a variable per structure class.",
    )
    _add(
        box,
        "group",
        dest="group",
        choices=["StrucGEDI", "StrucALS"],
        help="Group data by this column.",
    )
    _add(
        box,
        "group-var",
        dest="group_var",
        choices=GROUP_VARS,
        help="Variable shown in the boxplot.",
    )
    return parser


def _require(parser, args, flag, *names):
    """Stops with an error if options needed by an action are missing.

    Args:

        parser (argparse parser): parser used to report the error.

        args (argparse namespace): parsed options.

        flag (str): action that needs the options, e.g. boxplot.

        *names (str): names of the needed options.

    """
    missing = [n for n in names if not getattr(args, n)]
    if missing:
        opts = ", ".join("--" + n.replace("_", "-") for n in missing)
        parser.error(f"--{flag} requires {opts}.")


def gedisens(argv=None):
    """Runs the gedisens command line program.

    Args:

        argv (list): command line arguments, sys.argv is used if None.

    """
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s: %(message)s",
    )
    log = logging.getLogger("gedisens")

    actions = [
        args.layers,
        args.fhd,
        args.structure_plot,
        args.correlation_plot,
        args.boxplot,
    ]
    if not any(actions):
        parser.error(
            "Choose at least one of --layers, --fhd, "
            "--structure-plot, --correlation-plot, --boxplot."
        )
    if args.structure_plot:
        _require(parser, args, "structure-plot", "shot_number")
    if args.correlation_plot:
        _require(parser, args, "correlation-plot", "x_var", "y_var")
    if args.boxplot:
        _require(parser, args, "boxplot", "group", "group_var")
    if (args.layers or args.fhd) and not args.output_dir:
        parser.error("--layers and --fhd require --out-dir.")

    data_file = Path(args.data_file)
    if not data_file.exists():
        parser.error(f"File {data_file} does not exist.")

    log.info("Reading %s", data_file)
    data = io.read_vector(data_file)
    out_dir = Path(args.output_dir) if args.output_dir else None
    prefix = args.attr_name

    if args.layers:
        log.info("Calculating layers from %s profiles", prefix)
        layers = profiles.get_max_height(data, args.height_col)
        layers = layers.apply(
            lambda row: structure.calc_layers(
                structure.calc_upper_percentage(row, prefix), prefix=prefix
            ),
            axis=1,
        )
        cols = [
            "max_height_upper",
            "max_height_lower",
            "amp_sum_total",
            "upper_percentage",
            "NoL",
        ]
        out = data.copy()
        out[[f"{c}_{prefix}" for c in cols]] = layers[cols].to_numpy()
        path = io.write_vector(out, out_dir / f"{data_file.stem}_layers")
        print(f"Layers written to {path}")

    if args.fhd:
        log.info("Calculating FHD from %s profiles", prefix)
        out = structure.calc_fhd(data, prefix)
        out = out.rename(columns={"fhd": f"fhd_{prefix}"})
        path = io.write_vector(out, out_dir / f"{data_file.stem}_fhd")
        print(f"FHD written to {path}")

    if args.structure_plot:
        path = plots.plot_gedi_als_structure(
            data,
            args.shot_number,
            args.dz,
            add_info=args.add_info,
            output_dir=args.output_dir,
        )
        if path:
            print(f"Structure plot written to {path}")

    if args.correlation_plot:
        df, model, _, r2, predictions, rmse = stats.ols_regression(
            data, y_var=args.y_var, x_var=args.x_var
        )
        path = plots.plot_correlation(
            df,
            args.x_var,
            args.y_var,
            model,
            r2,
            predictions,
            rmse,
            output_dir=args.output_dir,
        )
        if path:
            print(f"Correlation plot written to {path}")

    if args.boxplot:
        groups = stats.group_data(data, args.group, args.group_var)
        log.info("%d groups found", len(groups))
        path = plots.plot_boxplot(
            groups,
            stats.calc_variance(groups),
            output_dir=args.output_dir,
            ylabel=args.group_var,
        )
        if path:
            print(f"Boxplot written to {path}")


main = gedisens

if __name__ == "__main__":
    main()
