"""Handling of vertical GEDI and ALS profiles.

Profiles are stored as one column per height bin, named
``<prefix><lower>_<upper>`` (e.g. ``Amp3_4`` for the GEDI amplitude or
``Pulse3_4`` for the ALS returns between 3 and 4 m above ground).
"""

import re

import numpy as np
import pandas as pd


def profile_columns(df, prefix):
    """Returns the profile columns of a prefix sorted by height.

    Args:

        df (pandas dataframe): data containing profile columns.

        prefix (str): column prefix, in this study either Amp or Pulse.

    Returns: list of column names from the lowest to the highest bin.

    """
    pattern = re.compile(rf"^{re.escape(prefix)}(\d+)_(\d+)$")
    cols = [
        (int(m.group(1)), c) for c in df.columns if (m := pattern.match(c))
    ]
    return [c for _, c in sorted(cols)]


def get_waveform_series(df, dz, data_name):
    """Creates x (value) and y (height) series of a single-shot profile.

    Function can only handle a dataframe with a single shot.

    Args:

        df (pandas dataframe): one row, first column is the shot number,
                               the remaining columns are profile bins.

        dz (int): vertical step size in m.

        data_name (str): name of the value series, either Amplitude
                         or Pulse.

    Returns: pandas series of values and pandas series of bin centre
             heights.

    """
    n = len(df.columns)
    x_vector = pd.Series(df.iloc[0, 1:].to_numpy(float), name=data_name)
    y_vector = pd.Series(
        [dz * i + dz / 2 for i in range(1, n)], name="Elevation"
    )
    return x_vector, y_vector


def vector_preparation(df):
    """Converts a single-shot profile into indexed values.

    Empty bins above the highest non-zero bin are dropped. Bins are
    indexed from 1 (lowest bin) upwards.

    Args:

        df (pandas dataframe): one row with Shot_Numbe and profile columns.

    Returns: list of (bin index, value) tuples.

    """
    row = df.drop(columns="Shot_Numbe", errors="ignore").iloc[0]
    values = row.to_numpy(float)
    nonzero = np.flatnonzero(values)
    if nonzero.size:
        values = values[: nonzero[-1] + 1]
    return [(i, v) for i, v in enumerate(values, start=1)]


def get_max_height(df, height_col="RH_90"):
    """Determines upper and lower boundary of the upper sixth of the canopy.

    For layer calculation RH90 is used as max height by default.

    Args:

        df (pandas dataframe): data with a canopy height column.

        height_col (str): column used as max height. Default is RH_90.

    Returns: copy of the dataframe with max_height_upper and
             max_height_lower columns.

    """
    df = df.copy()
    df["max_height_upper"] = df[height_col].round().astype(int)
    df["max_height_lower"] = np.ceil(df.max_height_upper * 5 / 6).astype(int)
    return df
