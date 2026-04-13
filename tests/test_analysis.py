import pytest
import pandas as pd
import numpy as np
from src.analysis import (
    run_ols_regression, 
    check_stationarity, 
    calculate_rolling_beta, 
    estimate_var_forecast
)

def test_run_ols_regression():
    # Generate dummy data
    x = np.linspace(0, 10, 100)
    y = 2 * x + np.random.normal(0, 1, 100)
    df = pd.DataFrame({'y': y, 'x': x})
    
    results = run_ols_regression(df, 'y', 'x')
    assert results.params['x'] == pytest.approx(2, rel=0.1)
    assert results.rsquared > 0.8

def test_check_stationarity():
    # Linear trend is non-stationary
    np.random.seed(42)
    t = np.linspace(0, 1, 1000)
    series = 5 * t + np.random.normal(0, 0.1, 1000)
    p_value = check_stationarity(pd.Series(series))
    # p-value for trend is usually high in ADF if not detrended
    assert p_value > 0.05

def test_calculate_rolling_beta():
    # Dummy returns
    np.random.seed(42)
    x = np.random.normal(0.001, 0.02, 500)
    y = 0.5 * x + np.random.normal(0, 0.005, 500)
    df = pd.DataFrame({'y': y, 'x': x})
    
    rolling = calculate_rolling_beta(df, 'y', 'x', window=100)
    assert len(rolling) == 500
    assert rolling.iloc[-1] == pytest.approx(0.5, rel=0.2)

def test_estimate_var_forecast():
    # Generate 2 correlated AR(1) processes
    np.random.seed(42)
    n = 100
    x = np.zeros(n)
    y = np.zeros(n)
    for t in range(1, n):
        x[t] = 0.5 * x[t-1] + np.random.normal(0, 0.1)
        y[t] = 0.3 * y[t-1] + 0.2 * x[t-1] + np.random.normal(0, 0.1)
    
    df = pd.DataFrame({'A': x, 'B': y})
    
    forecast = estimate_var_forecast(df, steps=5)
    assert forecast.shape == (5, 2)
