import oandapyV20
import oandapyV20.endpoints.instruments as instruments
from .config import Config

class OandaClient:
    def __init__(self):
        self.client = oandapyV20.API(access_token=Config.ACCESS_TOKEN, environment=Config.ENV)

    def get_candles(self, instrument, granularity, count=5000, from_time=None, to_time=None):
        """
        Fetch candle data from OANDA API.
        """
        params = {
            "granularity": granularity,
            "price": "M",  # Midpoint candles
        }
        if count:
            params["count"] = count
        if from_time:
            params["from"] = from_time
        if to_time:
            params["to"] = to_time

        r = instruments.InstrumentsCandles(instrument=instrument, params=params)
        self.client.request(r)
        return r.response.get("candles", [])
