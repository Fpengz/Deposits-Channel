import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def fetch_market_data(ticker: str, period: str = "5y") -> pd.DataFrame:
    """
    Fetches market data from Yahoo Finance as a fallback for FRED.
    Common tickers:
    - '^IRX': 13 Week Treasury Bill (Yield)
    - '^FVX': 5 Year Treasury Note (Yield)
    - '^TNX': 10 Year Treasury Note (Yield)
    - 'XLB': Materials Select Sector SPDR Fund (Proxy for bank assets/deposits)
    """
    try:
        data = yf.download(ticker, period=period)
        if data.empty:
            return pd.DataFrame()
        
        # yfinance returns multiple columns (Open, High, Low, Close, Adj Close, Volume)
        # We'll use 'Adj Close' as our 'value'
        df = data[['Adj Close']].copy()
        df.columns = ['value']
        df.index.name = 'date'
        return df
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return pd.DataFrame()

def get_proxy_fed_funds() -> pd.DataFrame:
    """Returns 13-week T-bill yield as a proxy for the Fed Funds Rate."""
    return fetch_market_data('^IRX')

def get_proxy_deposits() -> pd.DataFrame:
    """Returns an ETF or index as a proxy for banking sector activity."""
    # KBE is the SPDR S&P Bank ETF
    return fetch_market_data('KBE')
