import pytest
import pandas as pd
from unittest.mock import patch
import numpy as np
from src.data_fetcher import fetch_market_data, get_proxy_fed_funds, get_proxy_deposits

@patch('src.data_fetcher.yf.download')
def test_fetch_market_data(mock_download):
    # Mock MultiIndex columns that yfinance returns
    cols = pd.MultiIndex.from_tuples([('Close', '^IRX'), ('Adj Close', '^IRX')], names=['Price', 'Ticker'])
    df_mock = pd.DataFrame([[1.0, 1.1]], columns=cols, index=[pd.Timestamp('2023-01-01')])
    mock_download.return_value = df_mock
    
    df = fetch_market_data('^IRX')
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert 'value' in df.columns
    # With Adj Close available, it should pick it
    assert df.iloc[0]['value'] == 1.1

@patch('src.data_fetcher.fetch_market_data')
def test_get_proxies(mock_fetch):
    mock_fetch.return_value = pd.DataFrame({'value': [1.0]}, index=[pd.Timestamp('2023-01-01')])
    
    df_ff = get_proxy_fed_funds()
    df_dep = get_proxy_deposits()
    
    assert not df_ff.empty
    assert not df_dep.empty
    assert mock_fetch.call_count == 2
