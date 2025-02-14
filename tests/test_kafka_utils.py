import pytest
import os
from unittest.mock import patch, MagicMock
import time

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.kafka_utils import stream_single_trade

# Mock data to be returned by get_data and format_data functions
mock_data = {
    "BTC/USD": [{"time": "2024-12-01T00:00:00Z", "price": 42000}],
    "LTC/USD": [{"time": "2024-12-01T00:00:00Z", "price": 150}]
}
formatted_data = [
    {"time": "2024-12-01T00:00:00Z", "price": 42000, "symbol": "BTC/USD"},
    {"time": "2024-12-01T00:00:00Z", "price": 150, "symbol": "LTC/USD"}
]

@pytest.fixture
def producer():
    return MagicMock()

def test_stream_single_trade(producer):
    # Mock the necessary functions
    with patch('utils.kafka_utils.get_data', return_value=mock_data) as mock_get_data:
        with patch('utils.kafka_utils.format_data', return_value=formatted_data) as mock_format_data:
            with patch('time.sleep', return_value=None):
                # Call the function with mocked components
                stream_single_trade(producer, interval=0.1)

    # Check that get_data was called correctly
    mock_get_data.assert_called_once_with("BTC/USD,LTC/USD", "2024-12-01T00:00:00Z", limit=1000)
    
    # Check that format_data was called with the correct data
    mock_format_data.assert_called_once_with(mock_data)
    
    # Check that producer.send was called with the correct data
    assert producer.send.call_count == len(formatted_data)
    for obj in formatted_data:
        producer.send.assert_any_call('trading', obj)
    
    # Check that producer.flush was called once
    producer.flush.assert_called_once()
