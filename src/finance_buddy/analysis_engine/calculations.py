from typing import Dict
import pandas as pd

def calculate_metrics_from_alpha_vantage_data(daily_data: Dict[str, Dict]) -> Dict:
    """
    Takes raw daily data from Alpha Vantage and calculates key metrics.
    """
    if not daily_data or 'Time Series (Daily)' not in daily_data:
        return {}

    time_series = daily_data['Time Series (Daily)']

    # Convert to a pandas DataFrame for easier calculation
    try:
        df = pd.DataFrame.from_dict(time_series, orient='index')
        df.index = pd.to_datetime(df.index)
        df = df.rename(columns={
            '1. open': 'open',
            '2. high': 'high',
            '3. low': 'low',
            '4. close': 'close',
            '5. adjusted close': 'adjusted_close',
            '6. volume': 'volume',
            '7. dividend amount': 'dividend_amount',
            '8. split coefficient': 'split_coefficient'
        })
        df = df.astype(float)
        df = df.sort_index(ascending=True) # Sort from past to present
    except Exception as e:
        print(f"Error processing time series data: {e}")
        return {}

    if df.empty:
        return {}

    # Get the close prices
    close_prices = df['close']

    # Calculations
    high_52_week = close_prices.rolling(window=252, min_periods=1).max().iloc[-1] if not close_prices.empty else 0
    low_52_week = close_prices.rolling(window=252, min_periods=1).min().iloc[-1] if not close_prices.empty else 0
    ma_50_day = close_prices.rolling(window=50, min_periods=1).mean().iloc[-1] if not close_prices.empty else 0
    ma_200_day = close_prices.rolling(window=200, min_periods=1).mean().iloc[-1] if not close_prices.empty else 0

    # Performance
    if len(close_prices) > 1:
        latest_price = close_prices.iloc[-1]

        price_30_days_ago = close_prices.iloc[-30] if len(close_prices) > 30 else close_prices.iloc[0]
        price_90_days_ago = close_prices.iloc[-90] if len(close_prices) > 90 else close_prices.iloc[0]

        perf_30_day = ((latest_price - price_30_days_ago) / price_30_days_ago) * 100 if price_30_days_ago != 0 else 0
        perf_90_day = ((latest_price - price_90_days_ago) / price_90_days_ago) * 100 if price_90_days_ago != 0 else 0
    else:
        perf_30_day = 0
        perf_90_day = 0

    return {
        "52_week_high": high_52_week,
        "52_week_low": low_52_week,
        "50_day_moving_average": ma_50_day,
        "200_day_moving_average": ma_200_day,
        "30_day_performance_pct": perf_30_day,
        "90_day_performance_pct": perf_90_day,
    }
