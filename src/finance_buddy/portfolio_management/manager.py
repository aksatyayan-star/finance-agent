# This module will be responsible for portfolio management.
from typing import Dict, List, Optional
from src.finance_buddy.user_profiling import database
from src.finance_buddy.data_ingestion import ingestor

def analyze_portfolio(user_id: str) -> Optional[Dict]:
    """
    Analyzes a user's portfolio to calculate current value and profit/loss.
    """
    profile = database.get_user_profile(user_id)
    if not profile or not profile.portfolio:
        return {"error": "User has no portfolio to analyze."}

    total_portfolio_value = 0
    total_purchase_value = 0
    holdings_analysis = []

    for holding in profile.portfolio:
        quote_data = ingestor.get_stock_quote(holding.ticker_symbol)

        # Check if quote data is valid and contains the price
        if not quote_data or 'Global Quote' not in quote_data or not quote_data['Global Quote']:
            print(f"Could not retrieve quote for {holding.ticker_symbol}. Skipping.")
            continue

        try:
            current_price = float(quote_data['Global Quote']['05. price'])
        except (ValueError, KeyError):
            print(f"Could not parse price for {holding.ticker_symbol}. Skipping.")
            continue

        current_value = holding.quantity * current_price
        purchase_value = holding.quantity * holding.purchase_price
        profit_loss = current_value - purchase_value

        total_portfolio_value += current_value
        total_purchase_value += purchase_value

        holdings_analysis.append({
            "ticker": holding.ticker_symbol,
            "quantity": holding.quantity,
            "purchase_price": holding.purchase_price,
            "current_price": current_price,
            "current_value": current_value,
            "profit_loss": profit_loss
        })

    total_profit_loss = total_portfolio_value - total_purchase_value

    return {
        "holdings": holdings_analysis,
        "total_portfolio_value": total_portfolio_value,
        "total_purchase_value": total_purchase_value,
        "total_profit_loss": total_profit_loss
    }

def suggest_allocation(risk_tolerance: str) -> Dict[str, float]:
    """
    Suggests a simple asset allocation based on risk tolerance.
    """
    if risk_tolerance == 'low':
        return {"stocks": 0.4, "bonds": 0.5, "cash": 0.1}
    elif risk_tolerance == 'medium':
        return {"stocks": 0.6, "bonds": 0.3, "cash": 0.1}
    elif risk_tolerance == 'high':
        return {"stocks": 0.8, "bonds": 0.15, "cash": 0.05}
    else:
        # Default to a balanced allocation
        return {"stocks": 0.6, "bonds": 0.3, "cash": 0.1}
