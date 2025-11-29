import pandas as pd
from .strategy import Strategy

class BacktestEngine:
    def __init__(self, initial_balance=1000000):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.position = 0 # Current position size (units)
        self.trades = []

    def run(self, df: pd.DataFrame, strategy: Strategy):
        analyzed_df = strategy.analyze(df)
        
        # Vectorized backtest is faster, but event-driven is more accurate for real trading simulation.
        # For this MVP, we'll do a simple iteration to track P&L.
        
        for index, row in analyzed_df.iterrows():
            price = row['close']
            signal = row['signal'] # 1 (Bullish), -1 (Bearish)
            
            # Simple logic: Always be in the market based on signal
            # If signal is 1 and we are not long, Buy
            # If signal is -1 and we are not short, Sell
            
            target_position = 10000 * signal # Fixed lot size 10,000 units
            
            if self.position != target_position:
                # Execute trade
                trade_size = target_position - self.position
                # Cost/Profit calculation would happen here
                
                # Record trade
                self.trades.append({
                    "time": row['time'],
                    "type": "BUY" if trade_size > 0 else "SELL",
                    "price": price,
                    "size": abs(trade_size),
                    "balance": self.balance # Balance update requires P&L tracking
                })
                
                # Update P&L (Simplified: Mark to Market)
                # In a real engine, we'd track realized P&L on close.
                # Here, let's just track the "Value" of the portfolio
                
                self.position = target_position

        # Final Value
        last_price = analyzed_df.iloc[-1]['close']
        equity = self.balance + (self.position * (last_price - 0)) # Assuming 0 cost basis for simplicity in this draft
        # Wait, P&L = (Current Price - Entry Price) * Position
        # We need to track Entry Price.
        
        return self.calculate_performance(analyzed_df)

    def calculate_performance(self, df):
        # A better vectorized approach for P&L
        df['returns'] = df['close'].pct_change()
        df['strategy_returns'] = df['signal'].shift(1) * df['returns'] # Shift 1 because signal determines NEXT period return
        
        df['cumulative_returns'] = (1 + df['strategy_returns']).cumprod()
        final_return = df['cumulative_returns'].iloc[-1]
        
        return {
            "final_return": final_return,
            "total_trades": len(df[df['signal'].diff() != 0])
        }
