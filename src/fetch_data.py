from .oanda_client import OandaClient
from .db import Database
from .config import Config

def fetch_and_save(instrument="USD_JPY", granularity="M1", count=100):
    print(f"Fetching {count} candles for {instrument} ({granularity})...")
    
    try:
        Config.validate()
        client = OandaClient()
        db = Database()

        candles = client.get_candles(instrument, granularity, count=count)
        db.save_candles(instrument, granularity, candles)
        
        db.close()
        print("Done.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Example usage
    fetch_and_save()
