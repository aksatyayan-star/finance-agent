import unittest
from unittest.mock import patch
import pandas as pd

from src.finance_buddy.analysis_engine import calculations, analyzer

class TestAnalysisEngine(unittest.TestCase):

    def test_calculate_metrics(self):
        # Create a sample DataFrame similar to what Alpha Vantage would produce
        dates = pd.to_datetime(pd.date_range(end='2023-10-27', periods=252, freq='D'))
        data = {
            'Time Series (Daily)': {
                date.strftime('%Y-%m-%d'): {'4. close': str(150 + i*0.1)} for i, date in enumerate(dates)
            }
        }

        metrics = calculations.calculate_metrics_from_alpha_vantage_data(data)
        self.assertIsNotNone(metrics)
        self.assertIn('52_week_high', metrics)
        self.assertIn('50_day_moving_average', metrics)
        self.assertGreater(metrics['52_week_high'], 150)

    @patch('src.finance_buddy.data_ingestion.ingestor.get_historical_data')
    @patch('src.finance_buddy.data_ingestion.ingestor.get_cpi')
    @patch('src.finance_buddy.data_ingestion.ingestor.get_gdp')
    @patch('src.finance_buddy.data_ingestion.ingestor.get_financial_news')
    def test_analyze_stock(self, mock_news, mock_gdp, mock_cpi, mock_historical):
        # Mock the return values of the data ingestion functions
        mock_historical.return_value = {
            'Time Series (Daily)': {
                '2023-10-27': {'4. close': '170.00'},
                '2023-01-01': {'4. close': '150.00'}
            }
        }
        mock_cpi.return_value = {'observations': [{'date': '2023-09-01', 'value': '307.481'}]}
        mock_gdp.return_value = {'observations': [{'date': '2023-07-01', 'value': '22151.4'}]}
        mock_news.return_value = {'articles': [{'title': 'Big news for AAPL!'}]}

        report = analyzer.analyze_stock('AAPL')

        # Check that the report is structured correctly
        self.assertEqual(report['ticker'], 'AAPL')
        self.assertIn('stock_metrics', report)
        self.assertIn('economic_context', report)
        self.assertIn('news', report)

        # Check that the metrics were calculated
        self.assertGreater(report['stock_metrics']['52_week_high'], 0)

        # Check that economic data is present
        self.assertEqual(report['economic_context']['latest_cpi']['value'], '307.481')

        # Check that news is present
        self.assertEqual(report['news'][0]['title'], 'Big news for AAPL!')

if __name__ == '__main__':
    unittest.main()
