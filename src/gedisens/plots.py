"""Plots comparing GEDI and ALS vertical structure."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from gedisens.profiles import get_waveform_series, vector_preparation
from gedisens.stats import Stats

BOX = dict(facecolor="1", edgecolor="black", pad=5)


def _finish(fig, output_dir, filename, dpi=300):
    """Saves the figure to output_dir or shows it.

    Args:

        fig (matplotlib figure): figure to save.

        output_dir (str): where plot is saved, shown if empty.

        filename (str): name of the image file.

        dpi (int): resolution of the image. Default is 300.

    Returns: path of the saved file, None if the plot is shown.

    """
    if output_dir:
        path = Path(output_dir) / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        plt.close(fig)
        return path
    plt.show()
    return None


def _value(df, col):
    """Returns the value of a column of a single-row dataframe.

    Args:

        df (pandas dataframe): one row.

        col (str): column name.

    Returns: value as float.

    """
    return float(df[col].iloc[0])


def plot_gedi_als_structure(df, shot_number, dz=1, add_info="", output_dir=""):
    """Plot GEDI and ALS amplitude/pulse vertical structure.

    Command: plot_gedi_als_structure(df, shot_number="35070600200401943",
                                     dz=1, add_info="fhd", output_dir=".")

    Args:

        df (pandas dataframe): data with Amp and Pulse columns.

        shot_number (str): shot_number of interest in df.

        dz (int): vertical step size. Default is 1.
                  if other vertical steps are calculated
                  other dz can be used.

        add_info (str): optional info shown in the plot:
                        fhd: fhd values are broadcasted.
                        numb_lay: number of layer values are broadcasted.
                        stdv_var: stdv and variance are broadcasted.

        output_dir (str): where plot is saved, shown if empty.

    Returns: Plot with GEDI and ALS structure and calculated features of
             footprint.

    """
    shot_number = str(shot_number)
    df = df[df["Shot_Numbe"].astype(str) == shot_number]
    if df.empty:
        raise ValueError(f"Shot number {shot_number} not found in data.")

    # tree height from 1m to 50m
    pulse_cols = [f"Pulse{i}_{i + dz}" for i in range(1, 50, dz)]
    amp_cols = [f"Amp{i}_{i + dz}" for i in range(1, 50, dz)]
    als_df = df[["Shot_Numbe"] + pulse_cols]
    gedi_df = df[["Shot_Numbe"] + amp_cols]

    fig, ax1 = plt.subplots(figsize=(30, 30))

    x_als, y_als = get_waveform_series(als_df, dz, data_name="Pulse")
    x_gedi, y_gedi = get_waveform_series(gedi_df, dz, data_name="Amplitude")

    wave_amp = pd.concat([y_gedi, x_gedi], axis=1)
    wave_amp = wave_amp[wave_amp.Amplitude > 0]
    wave_amp["Amplitude"] = wave_amp.Amplitude / wave_amp.Amplitude.sum() * 100

    # ALS plot
    h1 = ax1.barh(
        y_als,
        x_als,
        height=dz - 0.3,
        color="forestgreen",
        alpha=0.75,
        label="ALS return",
    )
    # GEDI plot
    ax2 = ax1.twiny()
    (h2,) = ax2.plot(
        wave_amp.Amplitude,
        wave_amp.Elevation,
        color="black",
        linewidth=4,
        label="GEDI waveform",
    )

    ax1.set_xlabel("ALS returns [%]", fontsize=30, labelpad=14)
    ax1.set_ylabel("Height [m]", fontsize=30, labelpad=14)
    ax1.set_ylim(0, 51)
    ax1.set_yticks(range(0, 51, 5))
    ax1.grid()
    ax1.tick_params(labelsize=30)

    ax2.set_xlabel("GEDI amplitude [%]", fontsize=30, labelpad=14)
    ax2.set_xlim(0, 10)
    ax2.tick_params(labelsize=30)

    lines = [f"GEDI shot ID: {shot_number}"]
    y = 0.9
    if add_info == "fhd":
        lines += [
            r"GEDI FHD$_{\mathrm{L2B}}$:  "
            f"{round(_value(df, 'gediFHDl2b'), 2)}",
            r"GEDI FHD$_{\mathrm{calc}}$: " f"{_value(df, 'gediFHDcal')}",
            f"ALS FHD :  {_value(df, 'alsFHD')}",
            r"ALS$_{\mathrm{co}}$ FHD :  " f"{_value(df, 'alsFHDco')}",
        ]
        y = 0.85
    elif add_info == "numb_lay":
        lines += [
            f"GEDI NoL: {int(_value(df, 'NoL_GEDI'))}",
            r"ALS$_{\mathrm{co}}$ NoL: " f"{int(_value(df, 'NoL_ALS'))}",
        ]
    elif add_info == "stdv_var":
        gedi = Stats(vector_preparation(gedi_df))
        als = Stats(vector_preparation(als_df))
        lines += [
            f"GEDI variance: {round(gedi.variance, 2)}",
            f"GEDI stdv: {round(gedi.stdv, 2)}",
            r"ALS$_{\mathrm{co}}$ variance: " f"{round(als.variance, 2)}",
            r"ALS$_{\mathrm{co}}$ stdv: " f"{round(als.stdv, 2)}",
        ]
        y = 0.85

    ax2.set_title(
        "\n".join(lines), loc="right", fontsize=30, x=0.97, y=y, bbox=BOX
    )

    fig.legend(
        (h1, h2),
        ("ALS", "GEDI"),
        loc="lower right",
        bbox_to_anchor=(0.899, 0.13),
        fontsize=30,
    )

    return _finish(fig, output_dir, f"GEDIamp_vs_ALSpulse_{shot_number}.png")


def plot_correlation(
    df, x_var, y_var, model, r2, predictions, rmse, output_dir=""
):
    """Plot correlation between two variables.

    Args:

        df (pandas dataframe): containing the variables.

        x_var (str): use ALS variable here.

        y_var (str): use GEDI variable here.

        model (Regression Wrapper): statsmodels output.

        r2 (float): R squared of OLS model.

        predictions (pandas series): predictions of the variable.

        rmse (float): root mean squared error of estimation.

        output_dir (str): where plot is saved, shown if empty.

    Returns: Correlation plot.

    """
    fig, ax = plt.subplots(figsize=(20, 15))

    ax.axline((1, 1), slope=1, color="black", linewidth=4, linestyle="--")
    ax.plot(
        df[x_var],
        df[y_var],
        linestyle="none",
        marker=".",
        markersize=15,
        label=f"data points: {len(df)}",
    )

    intercept, slope = model.params.iloc[0], model.params.iloc[1]
    ax.plot(
        df[x_var],
        predictions,
        linewidth=8,
        color="red",
        label=f"Regression line: y = {intercept:.2f} + {slope:.2f}x",
    )
    ax.plot([], [], marker="", label=f"RMSE: {rmse}", color="None")
    ax.plot([], [], marker="", label=f"R²: {r2}", color="None")

    ax.tick_params(axis="both", labelsize=20)
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.set_xlabel(x_var, fontsize=25)
    ax.set_ylabel(y_var, fontsize=25)
    ax.set_title(f"Correlation of {x_var} and {y_var}", fontsize=30)
    ax.legend(fontsize=25, markerscale=2, loc="lower right", labelspacing=1)
    ax.grid()

    return _finish(fig, output_dir, f"correlation_plot_{y_var}_vs_{x_var}.png")


def plot_boxplot(
    data,
    variance,
    output_dir="",
    labels=("low", "medium", "high"),
    ylabel="FHD",
):
    """Plots values separated into interpreted structure.

    Args:

        data (list): list of values separated in structure.

        variance (list): list of variance for each category.

        output_dir (str): where plot is saved, shown if empty.

        labels (tuple): x tick labels of the structure classes.
                        Default is low, medium, high.

        ylabel (str): y axis label. Default is FHD.

    Returns: Boxplot.

    """
    fig, ax = plt.subplots(figsize=(15, 12))

    meanpointprops = dict(
        marker="D",
        markeredgecolor="black",
        markerfacecolor="firebrick",
        markersize=20,
    )
    bp = ax.boxplot(data, meanprops=meanpointprops, showmeans=True)

    for median in bp["medians"]:
        median.set(color="black", linewidth=2)
    for artist in bp["whiskers"] + bp["caps"]:
        artist.set(linewidth=2)

    ax.set_xlabel("Structure", fontsize=25)
    ax.set_ylabel(ylabel, fontsize=25)
    ax.tick_params("both", labelsize=20)
    ax.set_xticks(range(1, len(data) + 1), list(labels)[: len(data)])
    ax.grid()

    for i, (values, vari) in enumerate(zip(data, variance, strict=True)):
        xpos = bp["medians"][i].get_xdata()
        mean = bp["means"][i].get_ydata()[0]
        xoff = 0.1 * (xpos[1] - xpos[0])
        capbottom = bp["caps"][2 * i].get_ydata()[0]
        text = dict(fontsize=20, fontweight="bold")

        ax.text(
            xpos[1] - xoff,
            capbottom,
            f"n = {len(values)}",
            va="center",
            **text,
        )
        ax.text(xpos[1] + xoff, mean, f"mean = {mean:.2f}", **text)
        ax.text(
            xpos[1] + xoff,
            mean - 0.05,
            f"variance = {vari}",
            va="center",
            **text,
        )
        ax.scatter(np.repeat(i + 1, len(values)), values, s=50)

    return _finish(fig, output_dir, "boxplot.png")
