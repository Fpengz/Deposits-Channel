import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
import pandas as pd

def run_ols_regression(df: pd.DataFrame, y_col: str, x_col: str):
    """Performs OLS regression and returns the model results."""
    y = df[y_col]
    x = sm.add_constant(df[x_col])
    model = sm.OLS(y, x).fit()
    return model

def check_stationarity(series: pd.Series) -> float:
    """Runs ADF test and returns the p-value."""
    result = adfuller(series.dropna())
    return result[1] # p-value
