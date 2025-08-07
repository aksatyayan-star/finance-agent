import unittest
import json
from pathlib import Path
from unittest.mock import patch

from src.finance_buddy.user_profiling.profile import UserProfile, FinancialGoal
from src.finance_buddy.user_profiling import database
from src.finance_buddy.user_profiling import assessment

class TestUserProfiling(unittest.TestCase):

    def setUp(self):
        """Set up a temporary database for testing."""
        self.test_db_file = Path(__file__).parent / 'test_user_profiles.json'
        # Ensure the file is clean before each test
        if self.test_db_file.exists():
            self.test_db_file.unlink()

        # Patch the DB_FILE constant in the database module
        self.db_patcher = patch('src.finance_buddy.user_profiling.database.DB_FILE', self.test_db_file)
        self.db_patcher.start()

    def tearDown(self):
        """Clean up the temporary database file."""
        if self.test_db_file.exists():
            self.test_db_file.unlink()
        self.db_patcher.stop()

    def test_user_profile_creation(self):
        goal = FinancialGoal(goal_name="Retirement", target_amount=1000000.0)
        profile = UserProfile(
            user_id="test_user",
            risk_tolerance="medium",
            investment_horizon=20,
            annual_income=80000.0,
            financial_goals=[goal]
        )
        self.assertEqual(profile.user_id, "test_user")
        self.assertEqual(profile.financial_goals[0].goal_name, "Retirement")

    def test_db_create_and_get_user(self):
        goal = FinancialGoal(goal_name="Buy a house", target_amount=50000.0)
        profile = UserProfile("db_user", "high", 10, 120000.0, [goal])

        # Test creation
        self.assertTrue(database.create_user(profile))

        # Test retrieval
        retrieved_profile = database.get_user_profile("db_user")
        self.assertIsNotNone(retrieved_profile)
        self.assertEqual(retrieved_profile.user_id, "db_user")
        self.assertEqual(retrieved_profile.annual_income, 120000.0)
        self.assertEqual(len(retrieved_profile.financial_goals), 1)
        self.assertEqual(retrieved_profile.financial_goals[0].target_amount, 50000.0)

    def test_db_update_user(self):
        profile = UserProfile("update_user", "low", 30, 60000.0, [])
        database.create_user(profile)

        updates = {"annual_income": 65000.0, "risk_tolerance": "medium"}
        self.assertTrue(database.update_user_profile("update_user", updates))

        updated_profile = database.get_user_profile("update_user")
        self.assertEqual(updated_profile.annual_income, 65000.0)
        self.assertEqual(updated_profile.risk_tolerance, "medium")

    def test_risk_assessment(self):
        # Test low risk
        low_answers = {'q1': 1, 'q2': 1, 'q3': 1}
        self.assertEqual(assessment.assess_risk_tolerance(low_answers), 'low')

        # Test medium risk
        medium_answers = {'q1': 2, 'q2': 2, 'q3': 2}
        self.assertEqual(assessment.assess_risk_tolerance(medium_answers), 'medium')

        # Test high risk
        high_answers = {'q1': 3, 'q2': 3, 'q3': 3}
        self.assertEqual(assessment.assess_risk_tolerance(high_answers), 'high')

if __name__ == '__main__':
    unittest.main()
