import pytest
from unittest.mock import MagicMock, patch
from src.oanda_client import OandaClient
from src.db import Database
import os

# Mock Config
@pytest.fixture(autouse=True)
def mock_config():
    with patch("src.config.Config.ACCESS_TOKEN", "mock_token"), \
         patch("src.config.Config.ACCOUNT_ID", "mock_id"), \
         patch("src.config.Config.ENV", "practice"):
        yield

def test_oanda_client_get_candles():
    with patch("oandapyV20.API") as MockAPI:
        mock_api_instance = MockAPI.return_value
        # Mock response
        mock_api_instance.request.return_value = None # request returns nothing, but modifies the request object
        # We need to mock the request object passed to client.request
        
        # Simpler approach: Mock the request method of the client instance
        client = OandaClient()
        client.client.request = MagicMock()
        
        # Mock the response attribute of the request object that instruments.InstrumentsCandles returns
        # But instruments.InstrumentsCandles is a class instantiation.
        
        with patch("src.oanda_client.instruments.InstrumentsCandles") as MockCandles:
            mock_r = MockCandles.return_value
            mock_r.response = {"candles": [{"time": "2023-01-01", "mid": {"o": "100", "h": "101", "l": "99", "c": "100"}, "volume": 1}]}
            
            candles = client.get_candles("USD_JPY", "M1")
            assert len(candles) == 1
            assert candles[0]["time"] == "2023-01-01"

def test_database_save_candles(tmp_path):
    db_file = tmp_path / "test.db"
    db = Database(str(db_file))
    
    candles = [
        {"time": "2023-01-01T00:00:00Z", "mid": {"o": "100.0", "h": "101.0", "l": "99.0", "c": "100.5"}, "volume": 10}
    ]
    
    db.save_candles("USD_JPY", "M1", candles)
    
    conn = db.conn
    cursor = conn.execute("SELECT * FROM candles")
    rows = cursor.fetchall()
    
    assert len(rows) == 1
    assert rows[0][0] == "USD_JPY"
    assert rows[0][3] == 100.0
    
    db.close()
