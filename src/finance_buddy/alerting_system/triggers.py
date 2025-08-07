from typing import Dict, Optional

def check_price_movement(historical_data: Dict, threshold: float = 5.0) -> Optional[str]:
    """
    Checks if the latest daily price change exceeds a percentage threshold.
    """
    if not historical_data or 'Time Series (Daily)' not in historical_data:
        return None

    time_series = historical_data['Time Series (Daily)']
    dates = sorted(time_series.keys(), reverse=True)

    if len(dates) < 2:
        return None

    try:
        latest_close = float(time_series[dates[0]]['4. close'])
        previous_close = float(time_series[dates[1]]['4. close'])
    except (ValueError, KeyError):
        return None

    if previous_close == 0:
        return None

    percent_change = ((latest_close - previous_close) / previous_close) * 100

    if abs(percent_change) > threshold:
        direction = "up" if percent_change > 0 else "down"
        return f"Significant price movement detected: {percent_change:.2f}% {direction} in the last day."
    return None

def check_major_news(news_data: Dict) -> Optional[str]:
    """
    Checks for any recent news and returns an alert.
    (A more sophisticated version could analyze sentiment or source).
    """
    if news_data and news_data.get('totalResults', 0) > 0:
        latest_article = news_data['articles'][0]
        return f"Major news event: '{latest_article['title']}'"
    return None

def check_technical_levels(stock_metrics: Dict, current_price: float, proximity_threshold: float = 0.02) -> Optional[str]:
    """
    Checks if the current price is close to the 50-day or 200-day moving average.
    """
    if not stock_metrics:
        return None

    ma_50 = stock_metrics.get("50_day_moving_average")
    ma_200 = stock_metrics.get("200_day_moving_average")

    if ma_50 and ma_50 > 0 and abs(current_price - ma_50) / ma_50 < proximity_threshold:
        return f"Price is approaching its 50-day moving average ({ma_50:.2f})."

    if ma_200 and ma_200 > 0 and abs(current_price - ma_200) / ma_200 < proximity_threshold:
        return f"Price is approaching its 200-day moving average ({ma_200:.2f})."

    return None
