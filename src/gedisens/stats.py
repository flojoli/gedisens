import numpy as np
import math
import statsmodels.api as sm
from sklearn.metrics import mean_squared_error


def ols_regression(df,y_var,x_var,reconstr=False):
    """Calculates OLS regression.

    Parameters
    ----------
    df : dataframe
        Pandas dataframe containing filtered data.
    y_var : string
        y (dependent variable) in regression (use GEDI!)
    x_var : string
        x (independent variable) in regression (use ALS!)
    reconstr: boolean
        Whether to use reconstr or not. The default is False.

    Returns
    -------
    x
    r2
    predictions
    rmse
    """

    if reconstr == 'True':
        y_var='RH_100'
        print('--> Reconstruction of RH 100')
    else:
        y_var=y_var

    x = df[x_var]

    y = df[y_var]
    x = sm.add_constant(x)
    model = sm.OLS(y,x).fit()
    predictions= model.predict(x)

    rmse = np.sqrt(mean_squared_error(predictions,y)).round(2)
    r2 = round(model.rsquared,2)
    print('3. Regression: DONE')

    return df, model, x, r2, predictions, rmse


class Stats:
    """ Calculates statistics of discrete histogram."""

    def __init__(self,histindexed):

        self.n=len(histindexed)
        self.sum=0
        self.elev=0
        self.sqsum=0
        for x,y in histindexed:
            self.sum+=y
            self.elev+=x*y

        self.mean=self.elev/self.sum
        for x,y in histindexed:
            dx=x-self.mean
            self.sqsum+=y*dx*dx
        # σ²
        self.variance=(self.sqsum/self.sum)
        self.stdv=math.sqrt(self.variance)
