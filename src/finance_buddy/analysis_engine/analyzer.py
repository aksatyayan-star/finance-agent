# This module will contain the core financial analysis tools.
from src.finance_buddy.data_ingestion import ingestor
from . import calculations

def analyze_stock(ticker: str):
    """
    Performs a comprehensive analysis of a stock, including key metrics,
    economic context, and recent news.
    """
    # 1. Fetch data
    # We need a full year of data for 52-week metrics, so use 'full'
    historical_data = ingestor.get_historical_data(ticker, outputsize='full')
    cpi_data = ingestor.get_cpi()
    gdp_data = ingestor.get_gdp()
    news = ingestor.get_financial_news(ticker)

    if not historical_data:
        return {"error": f"Could not retrieve historical data for {ticker}."}

    # 2. Calculate metrics
    stock_metrics = calculations.calculate_metrics_from_alpha_vantage_data(historical_data)

    # 3. Structure the report
    analysis_report = {
        "ticker": ticker,
        "stock_metrics": stock_metrics,
        "economic_context": {
            # Get the most recent values for simplicity
            "latest_cpi": cpi_data.get('observations', [{}])[0] if cpi_data else {},
            "latest_gdp": gdp_data.get('observations', [{}])[0] if gdp_data else {},
        },
        "news": news.get('articles', []) if news else []
    }

    return analysis_report
