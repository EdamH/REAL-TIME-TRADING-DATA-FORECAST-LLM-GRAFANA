import os
import pytest
from unittest.mock import patch, mock_open
# Modify the path to include the parent directory
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.api_utils import get_data, format_data

# Mock environment variables
os.environ['flights_api_url'] = 'http://mockapi.com/'
os.environ['flights_api_key'] = 'mockapikey'

# Mock response data for the Alpaca API
mock_data = {
    "bars": {
        "BTC/USD": [
            {"time": "2025-02-08T00:00:00Z", "open": 30000, "close": 31000, "high": 31500, "low": 29500, "volume": 1000},
            {"time": "2025-02-08T01:00:00Z", "open": 31000, "close": 32000, "high": 32500, "low": 30500, "volume": 1500}
        ],
        "LTC/USD": [
            {"time": "2025-02-08T00:00:00Z", "open": 2000, "close": 2050, "high": 2100, "low": 1950, "volume": 500},
            {"time": "2025-02-08T01:00:00Z", "open": 2050, "close": 2100, "high": 2150, "low": 2000, "volume": 700}
        ]
    },
    "next_page_token": None  

}

# Modify the test to match the get_data API structure
@patch('utils.api_utils.requests.get')
def test_get_data(mock_get):
    
    mock_get.return_value.json.return_value = mock_data
    mock_get.return_value.status_code = 200
    # print(mock_data)
    symbols = 'BTC/USD,ETC/USD'
    start_date = '2025-02-08T00:00:00Z'
    end_date = '2025-02-08T02:00:00Z'
    response = get_data(symbols, start_date, end_date)
    print(f"HERE I AM! {response}")
    
    # Verify that data is fetched correctly for both BTCUSD and ETHUSD
    assert response['BTC/USD'] == mock_data['bars']['BTC/USD']
    assert response['LTC/USD'] == mock_data['bars']['LTC/USD']

def test_format_data():
    formatted_data = format_data(mock_data['bars'])
    expected_data = [
        {"time": "2025-02-08T00:00:00Z", "open": 30000, "close": 31000, "high": 31500, "low": 29500, "volume": 1000, "symbol": "BTC/USD"},
        {"time": "2025-02-08T01:00:00Z", "open": 31000, "close": 32000, "high": 32500, "low": 30500, "volume": 1500, "symbol": "BTC/USD"},
        {"time": "2025-02-08T00:00:00Z", "open": 2000, "close": 2050, "high": 2100, "low": 1950, "volume": 500, "symbol": "LTC/USD"},
        {"time": "2025-02-08T01:00:00Z", "open": 2050, "close": 2100, "high": 2150, "low": 2000, "volume": 700, "symbol": "LTC/USD"}
    ]
    
    assert formatted_data == expected_data

@pytest.fixture(autouse=True)
def run_around_tests():
    # Clean up any test artifacts before/after running tests
    yield
    if os.path.exists('utils/test_data.json'):
        os.remove('utils/test_data.json')
