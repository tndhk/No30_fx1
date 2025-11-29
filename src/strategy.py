import pandas as pd

class Strategy:
    def analyze(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze the dataframe and add a 'signal' column.
        1: Buy, -1: Sell, 0: Hold
        """
        raise NotImplementedError

class SMAStrategy(Strategy):
    def __init__(self, short_window=10, long_window=30):
        self.short_window = short_window
        self.long_window = long_window

    def analyze(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['short_mavg'] = df['close'].rolling(window=self.short_window, min_periods=1).mean()
        df['long_mavg'] = df['close'].rolling(window=self.long_window, min_periods=1).mean()
        
        df['signal'] = 0
        # Create a signal when short MA crosses above long MA
        # Use shift to avoid lookahead bias if we were trading bar-by-bar, 
        # but for vector backtest we usually calculate signal based on completed bars.
        
        # Condition: Short > Long
        condition = df['short_mavg'] > df['long_mavg']
        
        # Signal: 1 where condition is True, -1 where False (or 0)
        # Simple crossover logic:
        # Buy (1) when Short crosses above Long
        # Sell (-1) when Short crosses below Long
        
        df['signal'] = 0
        df.loc[condition, 'signal'] = 1
        df.loc[~condition, 'signal'] = -1
        
        # Detect crossovers (change in signal)
        df['position'] = df['signal'].diff()
        
        # position = 2 ( -1 -> 1 ) => Buy
        # position = -2 ( 1 -> -1 ) => Sell
        
        return df
