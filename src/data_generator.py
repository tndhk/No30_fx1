import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_dummy_data(days=30, granularity="H1", start_price=100.0, volatility=0.001):
    """
    Generate dummy OHLCV data using a random walk.
    """
    # Determine frequency string for pandas
    freq_map = {
        "M1": "1min",
        "M5": "5min",
        "M15": "15min",
        "H1": "1h",
        "D": "1D"
    }
    freq = freq_map.get(granularity, "1h")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    dates = pd.date_range(start=start_date, end=end_date, freq=freq)
    n = len(dates)
    
    # Random walk for Close price
    returns = np.random.normal(0, volatility, n)
    price_path = start_price * np.exp(np.cumsum(returns))
    
    # Generate OHLC based on Close
    # High is slightly higher, Low is slightly lower, Open is previous Close
    high = price_path * (1 + np.abs(np.random.normal(0, volatility/2, n)))
    low = price_path * (1 - np.abs(np.random.normal(0, volatility/2, n)))
    
    # Adjust Open to match previous Close (approx)
    open_p = np.roll(price_path, 1)
    open_p[0] = start_price
    
    # Ensure High is highest and Low is lowest
    high = np.maximum(high, np.maximum(open_p, price_path))
    low = np.minimum(low, np.minimum(open_p, price_path))
    
    df = pd.DataFrame({
        "time": dates,
        "open": open_p,
        "high": high,
        "low": low,
        "close": price_path,
        "volume": np.random.randint(100, 1000, n)
    })
    
    return df
