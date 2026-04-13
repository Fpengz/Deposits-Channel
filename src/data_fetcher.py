import requests
import pandas as pd

def fetch_fred_series(series_id: str, api_key: str) -> pd.DataFrame:
    """Fetches a time series from the FRED API and returns a Pandas DataFrame."""
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={api_key}&file_type=json"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    
    observations = data.get('observations', [])
    if not observations:
        return pd.DataFrame()
        
    df = pd.DataFrame(observations)
    df = df[df['value'] != '.'] # Handle missing values represented as '.'
    df['value'] = df['value'].astype(float)
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date')
    return df[['value']]
