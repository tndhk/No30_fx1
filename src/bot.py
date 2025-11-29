import time
import pandas as pd
from .config import Config
from .data_generator import generate_dummy_data
from .strategy import SMAStrategy
from .execution import OrderExecutor
from .notification import Notifier

class TradingBot:
    def __init__(self):
        self.strategy = SMAStrategy(short_window=5, long_window=10) # Shorter windows for demo
        self.executor = OrderExecutor() # Mock mode by default if env is not set
        self.notifier = Notifier()
        self.position = 0 # 0: Flat, 1: Long, -1: Short
        self.lot_size = 1000

    def run(self, iterations=10, interval=1):
        print("Starting Trading Bot (Mock Mode)...")
        self.notifier.send_message("🚀 Trading Bot Started (Mock Mode)")

        # Simulate a loop
        # In real life, we would fetch only the latest candle.
        # Here, we generate a growing dataset to simulate time passing.
        
        # Initial data
        df = generate_dummy_data(days=5, granularity="M1")
        
        for i in range(iterations):
            print(f"\n--- Iteration {i+1}/{iterations} ---")
            
            # 1. Fetch Data (Simulate new candle)
            # Append a new candle to df
            new_candle = generate_dummy_data(days=0, granularity="M1").iloc[-1:] # Hacky way to get 1 candle
            # Adjust time to be next minute
            last_time = df.iloc[-1]['time']
            new_candle['time'] = last_time + pd.Timedelta(minutes=1)
            
            # Concatenate
            df = pd.concat([df, new_candle], ignore_index=True)
            
            # 2. Analyze
            analyzed_df = self.strategy.analyze(df)
            latest_signal = analyzed_df.iloc[-1]['signal']
            current_price = analyzed_df.iloc[-1]['close']
            
            print(f"Time: {analyzed_df.iloc[-1]['time']}, Price: {current_price:.2f}, Signal: {latest_signal}")

            # 3. Execute
            # Logic: If signal is 1 and we are not Long, Buy.
            #        If signal is -1 and we are not Short, Sell.
            #        If signal is 0, do nothing (or close? Strategy defines hold as 0? No, usually 0 is no signal)
            #        Our SMA strategy returns 1 (Buy/Hold Long) or -1 (Sell/Hold Short).
            
            if latest_signal == 1 and self.position <= 0:
                print("Signal BUY detected.")
                # Close Short if any
                if self.position == -1:
                    self.executor.execute_order("USD_JPY", self.lot_size, type="BUY") # Close
                
                # Open Long
                order = self.executor.execute_order("USD_JPY", self.lot_size)
                self.notifier.send_trade_log(order)
                self.position = 1
                
            elif latest_signal == -1 and self.position >= 0:
                print("Signal SELL detected.")
                # Close Long if any
                if self.position == 1:
                    self.executor.execute_order("USD_JPY", -self.lot_size, type="SELL") # Close
                
                # Open Short
                order = self.executor.execute_order("USD_JPY", -self.lot_size)
                self.notifier.send_trade_log(order)
                self.position = -1
            else:
                print("No position change.")

            time.sleep(interval)

        print("Bot stopped.")
        self.notifier.send_message("🛑 Trading Bot Stopped")

if __name__ == "__main__":
    bot = TradingBot()
    bot.run()
