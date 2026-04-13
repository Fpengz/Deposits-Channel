import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def fetch_market_data(ticker: str, period: str = "5y") -> pd.DataFrame:
    """
    Fetches market data from Yahoo Finance as a fallback for FRED.
    """
    try:
        # download with auto_adjust=False to try and get Adj Close
        # But handle the MultiIndex that yfinance often returns now
        data = yf.download(ticker, period=period, auto_adjust=False)
        
        if data.empty:
            print(f"Warning: No data returned for ticker {ticker}")
            return pd.DataFrame()
        
        # yfinance >= 0.2.x often returns MultiIndex columns even for single tickers
        # Flatten MultiIndex if it exists
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
            
        # Try to use Adj Close, fall back to Close
        target_col = None
        if 'Adj Close' in data.columns:
            target_col = 'Adj Close'
        elif 'Close' in data.columns:
            target_col = 'Close'
            
        if target_col is None:
            print(f"Error: Neither 'Adj Close' nor 'Close' found in columns: {data.columns}")
            return pd.DataFrame()
            
        df = data[[target_col]].copy()
        df.columns = ['value']
        df.index.name = 'date'
        
        # Handle cases where value might be all NaN
        if df['value'].isnull().all():
            print(f"Warning: All values for {ticker} are NaN")
            return pd.DataFrame()
            
        return df
    except Exception as e:
        print(f"Exception fetching data for {ticker}: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

def get_proxy_fed_funds() -> pd.DataFrame:
    """Returns 13-week T-bill yield as a proxy for the Fed Funds Rate."""
    return fetch_market_data('^IRX')

def get_proxy_deposits() -> pd.DataFrame:
    """Returns an ETF or index as a proxy for banking sector activity."""
    # KBE is the SPDR S&P Bank ETF
    return fetch_market_data('KBE')

def get_proxy_regional_banks() -> pd.DataFrame:
    """Returns the iShares Regional Banks ETF (IAT) as a proxy."""
    return fetch_market_data('IAT')
