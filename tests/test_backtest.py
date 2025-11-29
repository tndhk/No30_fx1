import pytest
import pandas as pd
from src.strategy import SMAStrategy
from src.backtest import BacktestEngine
from src.data_generator import generate_dummy_data

def test_data_generator():
    df = generate_dummy_data(days=1, granularity="H1")
    assert not df.empty
    assert "close" in df.columns
    assert len(df) > 0

def test_sma_strategy():
    # Create a deterministic dataframe
    data = {
        "time": pd.date_range(start="2023-01-01", periods=5, freq="D"),
        "close": [100, 110, 120, 110, 100], # Up then Down
        "open": [100, 110, 120, 110, 100],
        "high": [100, 110, 120, 110, 100],
        "low": [100, 110, 120, 110, 100],
        "volume": [100, 100, 100, 100, 100]
    }
    df = pd.DataFrame(data)
    
    # Short window 2, Long window 3
    strategy = SMAStrategy(short_window=2, long_window=3)
    analyzed_df = strategy.analyze(df)
    
    assert "short_mavg" in analyzed_df.columns
    assert "long_mavg" in analyzed_df.columns
    assert "signal" in analyzed_df.columns
    
    # Check values manually
    # Close: 100, 110, 120, 110, 100
    # SMA2:  NaN, 105, 115, 115, 105
    # SMA3:  NaN, NaN, 110, 113.3, 110
    
    # Index 2 (120): SMA2(115) > SMA3(110) -> Signal 1
    # Index 3 (110): SMA2(115) > SMA3(113.3) -> Signal 1
    # Index 4 (100): SMA2(105) < SMA3(110) -> Signal -1
    
    assert analyzed_df.iloc[2]['signal'] == 1
    assert analyzed_df.iloc[4]['signal'] == -1

def test_backtest_engine():
    # Create a scenario where price goes up, signal is 1
    data = {
        "time": pd.date_range(start="2023-01-01", periods=10, freq="D"),
        "close": [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
        "open": [100] * 10, "high": [100] * 10, "low": [100] * 10, "volume": [100] * 10
    }
    df = pd.DataFrame(data)
    
    # Mock strategy that always buys
    class BuyStrategy(SMAStrategy):
        def analyze(self, df):
            df = df.copy()
            df['signal'] = 1
            return df
            
    engine = BacktestEngine()
    result = engine.run(df, BuyStrategy())
    
    assert result["final_return"] > 1.0 # Should be positive
