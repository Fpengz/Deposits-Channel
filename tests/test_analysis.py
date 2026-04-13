import pytest
import pandas as pd
import numpy as np
from src.analysis import run_ols_regression, check_stationarity

def test_run_ols_regression():
    # Generate dummy data
    x = np.linspace(0, 10, 100)
    y = 2 * x + np.random.normal(0, 1, 100)
    df = pd.DataFrame({'y': y, 'x': x})
    
    results = run_ols_regression(df, 'y', 'x')
    assert results.params['x'] == pytest.approx(2, rel=0.1)
    assert results.rsquared > 0.8

def test_check_stationarity():
    # Random walk is non-stationary
    rw = np.cumsum(np.random.normal(0, 1, 100))
    df = pd.Series(rw)
    p_value = check_stationarity(df)
    # p-value for non-stationary series should be relatively high
    assert p_value > 0.05
