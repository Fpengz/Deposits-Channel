import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.api import VAR
import pandas as pd
import numpy as np

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

def calculate_rolling_beta(df: pd.DataFrame, y_col: str, x_col: str, window: int = 252) -> pd.Series:
    """Calculates rolling beta of y relative to x."""
    betas = []
    for i in range(len(df)):
        if i < window:
            betas.append(np.nan)
        else:
            sub = df.iloc[i-window:i]
            if sub[y_col].dropna().empty or sub[x_col].dropna().empty:
                betas.append(np.nan)
                continue
            res = run_ols_regression(sub, y_col, x_col)
            betas.append(res.params[x_col])
    return pd.Series(betas, index=df.index)

def estimate_var_forecast(df: pd.DataFrame, steps: int = 5) -> np.ndarray:
    """Fits a VAR model and forecasts future values."""
    data = df.dropna()
    model = VAR(data)
    # Ensure at least 1 lag is used
    results = model.fit(maxlags=15, ic='aic', trend='c')
    # If k_ar is 0, VAR isn't useful, but statsmodels might return it
    if results.k_ar == 0:
        results = model.fit(1)
        
    forecast = results.forecast(data.values[-results.k_ar:], steps)
    return forecast

def calculate_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Returns the correlation matrix of a dataframe."""
    return df.corr()
