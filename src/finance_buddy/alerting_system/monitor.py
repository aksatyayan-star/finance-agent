import uuid
from typing import List
from src.finance_buddy.user_profiling import database
from src.finance_buddy.data_ingestion import ingestor
from src.finance_buddy.analysis_engine import analyzer
from src.finance_buddy.user_profiling.profile import Alert
from . import triggers
from dataclasses import asdict

def run_monitoring_check():
    """
    Runs a check for all users and all their holdings, generating alerts
    for any triggered conditions.
    """
    all_profiles = database.get_all_user_profiles()
    for profile in all_profiles:
        for holding in profile.portfolio:
            # Use the analysis engine to get all data and metrics in one go
            analysis = analyzer.analyze_stock(holding.ticker_symbol)
            if "error" in analysis:
                continue

            stock_metrics = analysis.get("stock_metrics", {})
            news = analysis.get("news", [])

            quote = ingestor.get_stock_quote(holding.ticker_symbol)
            if not quote or 'Global Quote' not in quote or not quote['Global Quote']:
                continue
            current_price = float(quote['Global Quote']['05. price'])

            # Check all triggers
            alert_messages = []
            historical_data = ingestor.get_historical_data(holding.ticker_symbol) # Needed for price change
            price_alert = triggers.check_price_movement(historical_data)
            if price_alert: alert_messages.append(price_alert)

            news_alert = triggers.check_major_news({"articles": news, "totalResults": len(news)})
            if news_alert: alert_messages.append(news_alert)

            tech_alert = triggers.check_technical_levels(stock_metrics, current_price)
            if tech_alert: alert_messages.append(tech_alert)

            # Add alerts to the user's profile
            for msg in alert_messages:
                new_alert = Alert(alert_id=str(uuid.uuid4()), message=f"[{holding.ticker_symbol}] {msg}")
                database.add_alert(profile.user_id, new_alert)

def get_unread_alerts(user_id: str) -> List[Alert]:
    """
    Retrieves all unread alerts for a given user.
    """
    profile = database.get_user_profile(user_id)
    if not profile:
        return []
    return [alert for alert in profile.alerts if alert.status == 'unread']

def mark_alert_as_read(user_id: str, alert_id: str) -> bool:
    """
    Marks a specific alert as read for a given user.
    """
    profile = database.get_user_profile(user_id)
    if not profile:
        return False

    alert_found = False
    for alert in profile.alerts:
        if alert.alert_id == alert_id:
            alert.status = 'read'
            alert_found = True
            break

    if not alert_found:
        return False

    updated_data = {"alerts": [asdict(a) for a in profile.alerts]}
    return database.update_user_profile(user_id, updated_data)
