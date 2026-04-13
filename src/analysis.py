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

def calculate_cross_correlation(s1: pd.Series, s2: pd.Series, max_lag: int = 15):
    """Calculates cross-correlation between two series at various lags."""
    lags = range(-max_lag, max_lag + 1)
    # Ensure they are aligned and normalized for better correlation values
    s1_norm = (s1 - s1.mean()) / (s1.std() * len(s1))
    s2_norm = (s2 - s2.mean()) / s2.std()
    coeffs = np.correlate(s1_norm, s2_norm, mode='full')
    # Match the range of lags
    mid = len(coeffs) // 2
    coeffs = coeffs[mid - max_lag : mid + max_lag + 1]
    return list(lags), list(coeffs)

def detect_monetary_regimes(ff_series: pd.Series, window: int = 20) -> pd.Series:
    """Detects 'Hiking' vs 'Easing' regimes based on a rolling average of proxy changes."""
    # Smoothed change to avoid noise
    change = ff_series.diff().rolling(window=window).mean()
    regimes = pd.Series('Stable', index=ff_series.index)
    regimes[change > 0.0001] = 'Hiking'
    regimes[change < -0.0001] = 'Easing'
    return regimes
