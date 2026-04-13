import pytest
import pandas as pd
from unittest.mock import patch
from src.data_fetcher import fetch_fred_series

@patch('src.data_fetcher.requests.get')
def test_fetch_fred_series(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        'observations': [
            {'date': '2023-01-01', 'value': '4.33'}
        ]
    }
    df = fetch_fred_series('DFF', 'fake_api_key')
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    # Check if the column is 'value' and its value is float 4.33
    assert df.iloc[0]['value'] == 4.33
