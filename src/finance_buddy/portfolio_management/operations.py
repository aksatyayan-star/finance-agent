from typing import List, Optional
from src.finance_buddy.user_profiling import database
from src.finance_buddy.user_profiling.profile import PortfolioHolding, UserProfile

def add_holding(user_id: str, holding: PortfolioHolding) -> bool:
    """
    Adds a new holding to a user's portfolio.
    """
    profile = database.get_user_profile(user_id)
    if not profile:
        return False

    # Add the new holding
    profile.portfolio.append(holding)

    # Update the profile in the database
    # The database function expects a dict, so we convert the profile back
    from dataclasses import asdict
    updated_data = {"portfolio": [asdict(h) for h in profile.portfolio]}

    return database.update_user_profile(user_id, updated_data)

def remove_holding(user_id: str, ticker_symbol: str) -> bool:
    """
    Removes a holding from a user's portfolio by ticker symbol.
    """
    profile = database.get_user_profile(user_id)
    if not profile:
        return False

    # Find and remove the holding
    original_len = len(profile.portfolio)
    profile.portfolio = [h for h in profile.portfolio if h.ticker_symbol != ticker_symbol]

    if len(profile.portfolio) == original_len:
        # No holding was removed
        return False

    # Update the profile in the database
    from dataclasses import asdict
    updated_data = {"portfolio": [asdict(h) for h in profile.portfolio]}

    return database.update_user_profile(user_id, updated_data)

def view_portfolio(user_id: str) -> Optional[List[PortfolioHolding]]:
    """
    Retrieves a user's portfolio.
    """
    profile = database.get_user_profile(user_id)
    if profile:
        return profile.portfolio
    return None
