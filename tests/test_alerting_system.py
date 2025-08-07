import unittest
from unittest.mock import patch, MagicMock
from src.finance_buddy.alerting_system import triggers, monitor
from src.finance_buddy.user_profiling.profile import UserProfile, PortfolioHolding, Alert

class TestAlertingSystem(unittest.TestCase):

    def test_check_price_movement(self):
        # Test significant price increase
        data = {'Time Series (Daily)': {
            '2023-10-27': {'4. close': '105.0'},
            '2023-10-26': {'4. close': '100.0'}
        }}
        alert = triggers.check_price_movement(data, threshold=4.0)
        self.assertIn("Significant price movement detected: 5.00% up", alert)

        # Test no significant change
        data['Time Series (Daily)']['2023-10-27']['4. close'] = '101.0'
        alert = triggers.check_price_movement(data, threshold=4.0)
        self.assertIsNone(alert)

    def test_check_technical_levels(self):
        metrics = {"50_day_moving_average": 100.0, "200_day_moving_average": 120.0}

        # Test approaching 50-day MA
        alert = triggers.check_technical_levels(metrics, 101.0)
        self.assertIn("approaching its 50-day moving average", alert)

        # Test not approaching any MA
        alert = triggers.check_technical_levels(metrics, 110.0)
        self.assertIsNone(alert)

    @patch('src.finance_buddy.user_profiling.database.get_all_user_profiles')
    @patch('src.finance_buddy.analysis_engine.analyzer.analyze_stock')
    @patch('src.finance_buddy.data_ingestion.ingestor.get_stock_quote')
    @patch('src.finance_buddy.data_ingestion.ingestor.get_historical_data')
    @patch('src.finance_buddy.user_profiling.database.add_alert')
    def test_run_monitoring_check(self, mock_add_alert, mock_hist, mock_quote, mock_analyze, mock_get_users):
        # Setup mock data
        holding = PortfolioHolding(ticker_symbol='AAPL', quantity=10, purchase_price=100)
        profile = UserProfile(user_id='testuser', portfolio=[holding], risk_tolerance='high', investment_horizon=10, annual_income=100000)
        mock_get_users.return_value = [profile]

        mock_analyze.return_value = {
            "stock_metrics": {"50_day_moving_average": 102.0},
            "news": []
        }
        mock_quote.return_value = {'Global Quote': {'05. price': '101.0'}}
        mock_hist.return_value = {'Time Series (Daily)': {'2023-10-27': {'4. close': '101.0'}, '2023-10-26': {'4. close': '100.0'}}}

        monitor.run_monitoring_check()

        # Check that add_alert was called because the price is near the 50-day MA
        mock_add_alert.assert_called_once()
        call_args = mock_add_alert.call_args[0]
        self.assertEqual(call_args[0], 'testuser')
        self.assertIn("approaching its 50-day moving average", call_args[1].message)

if __name__ == '__main__':
    unittest.main()
