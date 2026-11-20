"""Vertical forest structure metrics: FHD and number of layers."""

import logging
import re

import numpy as np
import pandas as pd

from gedisens.profiles import profile_columns

logger = logging.getLogger(__name__)


def _bin(prefix, lower):
    """Builds the column name of a 1 m height bin.

    Args:

        prefix (str): column prefix, either Amp or Pulse.

        lower (int): lower boundary of the bin in m.

    Returns: column name, e.g. Pulse3_4.

    """
    return f"{prefix}{lower}_{lower + 1}"


def calc_upper_percentage(row, prefix="Pulse"):
    """Calculates the percentage of the profile contained in upper layer.

    Function will be passed to apply, therefore calculation is rowwise.
    Run get_max_height from gedisens.profiles first.

    Args:

        row (pandas series): one footprint with max_height_lower,
                             max_height_upper and profile columns.

        prefix (str): column prefix, either Amp or Pulse.
                      Default is Pulse.

    Returns: the row with amp_sum_total and upper_percentage added.

    """
    row = row.copy()
    available = set(row.index)
    upper_cols = [
        c
        for i in range(int(row.max_height_lower), int(row.max_height_upper))
        if (c := _bin(prefix, i - 1)) in available
    ]
    pattern = re.compile(rf"^{re.escape(prefix)}\d+_\d+$")
    total_cols = [c for c in row.index if pattern.match(c)]

    total = float(row[total_cols].sum())
    row["amp_sum_total"] = total
    row["upper_percentage"] = (
        round(float(row[upper_cols].sum()) / total, 2) if total > 0 else np.nan
    )
    return row


def calc_layers(row, lim_low=0.3, lim_up=0.5, prefix="Pulse"):
    """Calculates the number of layers (NoL) of a footprint.

    upper percentage < lim_low: 3 layers (multi-layered).
    upper percentage > lim_up: 1 layer.
    otherwise a window of one sixth of the canopy height is moved down
    the profile. If any window holds >= lim_low of the profile the
    footprint has 2 layers, otherwise 3. Footprints which fit none of the
    rules (e.g. canopy height <= 6 m) get NaN.

    Args:

        row (pandas series): output row of calc_upper_percentage.

        lim_low/lim_up (float): thresholds for applying which layer.
                                (default: 0.3; 0.5)

        prefix (str): column prefix, either Amp or Pulse.
                      Default is Pulse.

    Returns: the row with NoL added.

    """
    row = row.copy()
    upper = row.upper_percentage
    row["NoL"] = np.nan

    if pd.isna(upper):
        return row

    if upper < lim_low:
        row["NoL"] = 3
    elif upper > lim_up:
        row["NoL"] = 1
    elif lim_low <= upper < lim_up and row.max_height_upper > 6:
        start = int(np.ceil(row.max_height_upper / 6))
        max_search = int(row.max_height_lower) - start

        if start > max_search:
            row["NoL"] = 1
        else:
            row["NoL"] = 3
            available = set(row.index)
            for sextile in range(start, max_search + 1):
                window = [
                    c
                    for amp_up in range(sextile - start + 1, sextile + start)
                    if (c := _bin(prefix, amp_up)) in available
                ]
                if row[window].sum() / row.amp_sum_total >= lim_low:
                    row["NoL"] = 2
                    break

    logger.debug("Footprint %s: NoL=%s", row.get("Shot_Numbe"), row["NoL"])
    return row


def calc_fhd(df, attr_name):
    """Calculates foliage height diversity.

    FHD is the Shannon index of the profile. The ground bin
    <attr_name>0_1 is excluded. Works on any number of rows, footprints
    without signal get NaN.

    Args:

        df (pandas dataframe): data with profile columns.

        attr_name (str): name of attribute on which fhd is calculated,
                         either Amp or Pulse.

    Returns: copy of the dataframe with calculated fhd column.

    """
    ground = f"{attr_name}0_1"
    cols = [c for c in profile_columns(df, attr_name) if c != ground]
    if not cols:
        raise KeyError(f"No profile columns starting with '{attr_name}'.")

    values = df[cols].to_numpy(float)
    values = np.where(values > 0, values, 0.0)
    total = values.sum(axis=1, keepdims=True)

    with np.errstate(divide="ignore", invalid="ignore"):
        p = values / total
        terms = np.where(p > 0, p * np.log(p), 0.0)
    fhd = -terms.sum(axis=1)
    fhd[total[:, 0] == 0] = np.nan

    out = df.copy()
    out["fhd"] = np.round(fhd, 2)
    return out
