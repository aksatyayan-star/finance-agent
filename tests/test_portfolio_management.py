import unittest
from unittest.mock import patch, MagicMock
from src.finance_buddy.user_profiling.profile import UserProfile, PortfolioHolding
from src.finance_buddy.portfolio_management import operations, manager

class TestPortfolioManagement(unittest.TestCase):

    @patch('src.finance_buddy.user_profiling.database.get_user_profile')
    @patch('src.finance_buddy.user_profiling.database.update_user_profile')
    def test_add_holding(self, mock_update, mock_get):
        # Setup a mock user profile
        mock_profile = UserProfile(user_id='testuser', risk_tolerance='medium', investment_horizon=10, annual_income=80000)
        mock_get.return_value = mock_profile
        mock_update.return_value = True

        holding = PortfolioHolding(ticker_symbol='AAPL', quantity=10, purchase_price=150.0)

        result = operations.add_holding('testuser', holding)

        self.assertTrue(result)
        mock_get.assert_called_once_with('testuser')
        # Check that update was called with the new portfolio
        mock_update.assert_called_once()
        updated_portfolio = mock_update.call_args[0][1]['portfolio']
        self.assertEqual(len(updated_portfolio), 1)
        self.assertEqual(updated_portfolio[0]['ticker_symbol'], 'AAPL')


    @patch('src.finance_buddy.data_ingestion.ingestor.get_stock_quote')
    @patch('src.finance_buddy.user_profiling.database.get_user_profile')
    def test_analyze_portfolio(self, mock_get_profile, mock_get_quote):
        # Setup mock profile with holdings
        holdings = [
            PortfolioHolding(ticker_symbol='AAPL', quantity=10, purchase_price=150.0),
            PortfolioHolding(ticker_symbol='GOOG', quantity=5, purchase_price=2500.0)
        ]
        mock_profile = UserProfile(user_id='testuser', portfolio=holdings, risk_tolerance='high', investment_horizon=20, annual_income=150000)
        mock_get_profile.return_value = mock_profile

        # Mock the return value of get_stock_quote for each ticker
        def quote_side_effect(ticker):
            if ticker == 'AAPL':
                return {'Global Quote': {'05. price': '175.0'}}
            if ticker == 'GOOG':
                return {'Global Quote': {'05. price': '2800.0'}}
            return None
        mock_get_quote.side_effect = quote_side_effect

        report = manager.analyze_portfolio('testuser')

        self.assertIsNotNone(report)
        self.assertIn('holdings', report)
        self.assertEqual(len(report['holdings']), 2)
        self.assertAlmostEqual(report['total_portfolio_value'], 10 * 175.0 + 5 * 2800.0)
        self.assertAlmostEqual(report['total_profit_loss'], (10 * 25.0) + (5 * 300.0))

    def test_suggest_allocation(self):
        low_risk = manager.suggest_allocation('low')
        self.assertEqual(low_risk, {"stocks": 0.4, "bonds": 0.5, "cash": 0.1})

        high_risk = manager.suggest_allocation('high')
        self.assertEqual(high_risk, {"stocks": 0.8, "bonds": 0.15, "cash": 0.05})

if __name__ == '__main__':
    unittest.main()
