import json
from pathlib import Path
from typing import Dict, Optional, Any
from dataclasses import asdict

from .profile import UserProfile, FinancialGoal

DB_FILE = Path(__file__).parent.parent.parent.parent / 'data' / 'user_profiles.json'

def _load_db() -> Dict[str, Any]:
    """Loads the database from the JSON file."""
    if not DB_FILE.exists():
        return {}
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def _save_db(db: Dict[str, Any]):
    """Saves the database to the JSON file."""
    DB_FILE.parent.mkdir(exist_ok=True)
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=4)

def create_user(user_profile: UserProfile) -> bool:
    """
    Creates a new user profile and saves it to the database.
    Returns True if successful, False if user already exists.
    """
    db = _load_db()
    if user_profile.user_id in db:
        print(f"User with ID {user_profile.user_id} already exists.")
        return False

    db[user_profile.user_id] = asdict(user_profile)
    _save_db(db)
    return True

def get_user_profile(user_id: str) -> Optional[UserProfile]:
    """
    Retrieves a user profile from the database.
    """
    db = _load_db()
    user_data = db.get(user_id)
    if user_data:
        # Reconstruct the dataclass objects
        goals_data = user_data.pop('financial_goals', [])
        goals = [FinancialGoal(**g) for g in goals_data]
        return UserProfile(financial_goals=goals, **user_data)
    return None

def update_user_profile(user_id: str, updated_data: Dict[str, Any]) -> bool:
    """
    Updates an existing user profile.
    Returns True if successful, False if user does not exist.
    """
    db = _load_db()
    if user_id not in db:
        return False

    # Update the fields
    profile_data = db[user_id]
    for key, value in updated_data.items():
        if key in profile_data:
            profile_data[key] = value

    db[user_id] = profile_data
    _save_db(db)
    return True
