"""Statistics and grouping of the results."""

import math

import numpy as np
import statsmodels.api as sm


def ols_regression(df, y_var, x_var):
    """Calculates OLS regression.

    Zero values and NaNs are dropped before fitting.

    Args:

        df (pandas dataframe): data containing both variables.

        y_var (str): y (dependent variable) in regression (use GEDI!).

        x_var (str): x (independent variable) in regression (use ALS!).

    Returns: filtered dataframe, fitted model, design matrix, R squared,
             predictions and rmse.

    """
    df = df[(df[x_var] != 0) & (df[y_var] != 0)].dropna(subset=[x_var, y_var])
    x = sm.add_constant(df[x_var])
    y = df[y_var]
    model = sm.OLS(y, x).fit()
    predictions = model.predict(x)

    rmse = round(float(np.sqrt(np.mean((predictions - y) ** 2))), 2)
    r2 = round(float(model.rsquared), 2)

    return df, model, x, r2, predictions, rmse


def group_data(df, group, group_var):
    """Groups variable values by structure class and drops zeros and NaNs.

    Args:

        df (pandas dataframe): data.

        group (str): either StrucGEDI or StrucALS.

        group_var (str): variable which is grouped and plotted.

    Returns: list of grouped variable, one pandas series per group.

    """
    df = df[(df[group] != 0) & (df[group_var] != 0)]
    df = df.dropna(subset=[group, group_var])
    return [values for _, values in df.groupby(group)[group_var]]


def calc_variance(data):
    """Calculates variance of grouped variable.

    Args:

        data (list): list of grouped data.

    Returns: list of variance for each group.

    """
    return [round(group.var(), 2) for group in data]


class Stats:
    """Calculates statistics of discrete histogram.

    Args:

        histindexed (list): list of (position, weight) tuples.

    Attributes: n, sum, mean, variance and stdv of the histogram.

    """

    def __init__(self, histindexed):
        self.n = len(histindexed)
        self.sum = sum(w for _, w in histindexed)
        self.elev = sum(x * w for x, w in histindexed)

        if self.sum == 0:
            self.mean = self.variance = self.stdv = math.nan
            self.sqsum = 0
            return

        self.mean = self.elev / self.sum
        self.sqsum = sum(w * (x - self.mean) ** 2 for x, w in histindexed)
        # σ²
        self.variance = self.sqsum / self.sum
        self.stdv = math.sqrt(self.variance)
