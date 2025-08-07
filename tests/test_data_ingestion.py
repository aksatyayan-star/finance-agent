import unittest
from unittest.mock import patch, MagicMock
from src.finance_buddy.data_ingestion import ingestor

class TestDataIngestion(unittest.TestCase):

    @patch('src.finance_buddy.data_ingestion.ingestor._fetch_alpha_vantage_data')
    def test_get_stock_quote(self, mock_fetch):
        mock_fetch.return_value = {'Global Quote': {'05. price': '123.45'}}
        quote = ingestor.get_stock_quote('AAPL')
        self.assertEqual(quote['Global Quote']['05. price'], '123.45')
        mock_fetch.assert_called_once_with({'function': 'GLOBAL_QUOTE', 'symbol': 'AAPL'})

    @patch('src.finance_buddy.data_ingestion.ingestor._fetch_alpha_vantage_data')
    def test_get_historical_data(self, mock_fetch):
        mock_fetch.return_value = {'Time Series (Daily)': {'2023-10-27': {'4. close': '170.00'}}}
        data = ingestor.get_historical_data('AAPL')
        self.assertIn('Time Series (Daily)', data)
        mock_fetch.assert_called_once_with({
            'function': 'TIME_SERIES_DAILY_ADJUSTED',
            'symbol': 'AAPL',
            'outputsize': 'compact'
        })

    @patch('src.finance_buddy.data_ingestion.ingestor._fetch_alpha_vantage_data')
    def test_get_sp500_data(self, mock_fetch):
        mock_fetch.return_value = {'Time Series (Daily)': {'2023-10-27': {'4. close': '420.00'}}}
        data = ingestor.get_sp500_data()
        self.assertIn('Time Series (Daily)', data)
        mock_fetch.assert_called_once_with({
            'function': 'TIME_SERIES_DAILY_ADJUSTED',
            'symbol': 'SPY',
            'outputsize': 'compact'
        })

    @patch('src.finance_buddy.data_ingestion.ingestor._fetch_fred_data')
    def test_get_cpi(self, mock_fetch):
        mock_fetch.return_value = {'observations': [{'value': '300'}]}
        cpi = ingestor.get_cpi()
        self.assertEqual(cpi['observations'][0]['value'], '300')
        mock_fetch.assert_called_once_with('CPIAUCSL')

    @patch('src.finance_buddy.data_ingestion.ingestor._fetch_fred_data')
    def test_get_gdp(self, mock_fetch):
        mock_fetch.return_value = {'observations': [{'value': '28000'}]}
        gdp = ingestor.get_gdp()
        self.assertEqual(gdp['observations'][0]['value'], '28000')
        mock_fetch.assert_called_once_with('GDPC1')

    @patch('src.finance_buddy.data_ingestion.ingestor._fetch_fred_data')
    def test_get_unemployment_rate(self, mock_fetch):
        mock_fetch.return_value = {'observations': [{'value': '3.8'}]}
        rate = ingestor.get_unemployment_rate()
        self.assertEqual(rate['observations'][0]['value'], '3.8')
        mock_fetch.assert_called_once_with('UNRATE')

    @patch('src.finance_buddy.data_ingestion.ingestor.NewsApiClient')
    def test_get_financial_news(self, MockNewsApiClient):
        mock_api_instance = MockNewsApiClient.return_value
        mock_api_instance.get_top_headlines.return_value = {'status': 'ok', 'articles': []}

        news = ingestor.get_financial_news('market')
        self.assertEqual(news['status'], 'ok')
        mock_api_instance.get_top_headlines.assert_called_once_with(
            q='market', category='business', language='en'
        )

if __name__ == '__main__':
    unittest.main()
