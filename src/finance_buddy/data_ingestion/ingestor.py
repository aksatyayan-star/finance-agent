# This module will be responsible for ingesting data from various sources.
import requests
import json
from ..config import ALPHA_VANTAGE_API_KEY

BASE_URL = 'https://www.alphavantage.co/query'

def _fetch_alpha_vantage_data(params):
    """
    Fetches data from the Alpha Vantage API using the requests library.

    Args:
        params (dict): A dictionary of parameters for the API call.
                       Must include 'function'.

    Returns:
        dict: The JSON response from the API, or None if an error occurs.
    """
    # Add the API key to every request
    params['apikey'] = ALPHA_VANTAGE_API_KEY

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        data = response.json()

        # Alpha Vantage returns an 'Error Message' or 'Information' key if the call fails or has a note
        if "Error Message" in data:
            print(f"API Error for function {params.get('function')}: {data['Error Message']}")
            return None
        if "Information" in data:
            print(f"API Info for function {params.get('function')}: {data['Information']}")
            # This is often a rate-limit message, which we should probably not treat as a hard error
            # but for now, we will return None
            return None

        return data

    except requests.exceptions.RequestException as e:
        print(f"HTTP Request failed: {e}")
        return None
    except json.JSONDecodeError:
        print("Failed to decode JSON from response.")
        return None

def get_stock_quote(symbol: str):
    """
    Fetches a real-time stock quote for a given symbol.
    """
    params = {
        'function': 'GLOBAL_QUOTE',
        'symbol': symbol
    }
    return _fetch_alpha_vantage_data(params)

def get_historical_data(symbol: str, outputsize: str = 'compact'):
    """
    Fetches the daily adjusted time series (OHLCV) for a given symbol.
    outputsize can be 'compact' (last 100) or 'full' (20+ years).
    """
    params = {
        'function': 'TIME_SERIES_DAILY_ADJUSTED',
        'symbol': symbol,
        'outputsize': outputsize
    }
    return _fetch_alpha_vantage_data(params)

def get_sp500_data(outputsize: str = 'compact'):
    """
    Fetches historical data for the S&P 500 index (using SPY as a proxy).
    """
    return get_historical_data('SPY', outputsize)

# --- FRED Integration ---
from ..config import FRED_API_KEY

FRED_BASE_URL = 'https://api.stlouisfed.org/fred/'

def _fetch_fred_data(series_id):
    """
    Fetches data for a specific series from the FRED API.
    """
    params = {
        'series_id': series_id,
        'api_key': FRED_API_KEY,
        'file_type': 'json'
    }

    try:
        response = requests.get(f"{FRED_BASE_URL}series/observations", params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"HTTP Request failed: {e}")
        return None
    except json.JSONDecodeError:
        print("Failed to decode JSON from response.")
        return None

def get_cpi():
    """
    Fetches the Consumer Price Index (CPI) data. Series ID: CPIAUCSL
    """
    return _fetch_fred_data('CPIAUCSL')

def get_gdp():
    """
    Fetches the Real Gross Domestic Product (GDP) data. Series ID: GDPC1
    """
    return _fetch_fred_data('GDPC1')

def get_unemployment_rate():
    """
    Fetches the Unemployment Rate data. Series ID: UNRATE
    """
    return _fetch_fred_data('UNRATE')

# --- NewsAPI.org Integration ---
from newsapi import NewsApiClient
from ..config import NEWS_API_KEY

def get_financial_news(query: str):
    """
    Fetches financial news for a given query.
    """
    try:
        newsapi = NewsApiClient(api_key=NEWS_API_KEY)
        top_headlines = newsapi.get_top_headlines(q=query,
                                                  category='business',
                                                  language='en')
        return top_headlines
    except Exception as e:
        print(f"An error occurred while fetching news: {e}")
        return None
