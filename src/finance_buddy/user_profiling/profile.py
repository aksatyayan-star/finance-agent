from dataclasses import dataclass, field
from typing import List

@dataclass
class FinancialGoal:
    goal_name: str
    target_amount: float

@dataclass
class UserProfile:
    user_id: str
    risk_tolerance: str  # 'low', 'medium', 'high'
    investment_horizon: int  # in years
    annual_income: float
    financial_goals: List[FinancialGoal] = field(default_factory=list)
