from src.data_generator import generate_dummy_data
from src.strategy import SMAStrategy
from src.backtest import BacktestEngine

def main():
    print("Generating dummy data...")
    df = generate_dummy_data(days=30, granularity="H1", volatility=0.002)
    print(f"Generated {len(df)} candles.")
    
    print("Running SMA Strategy (Short=10, Long=30)...")
    strategy = SMAStrategy(short_window=10, long_window=30)
    
    print("Executing Backtest...")
    engine = BacktestEngine(initial_balance=1000000)
    result = engine.run(df, strategy)
    
    print("-" * 30)
    print("Backtest Results:")
    print(f"Final Return: {result['final_return']:.4f}")
    print(f"Total Trades: {result['total_trades']}")
    print("-" * 30)

if __name__ == "__main__":
    main()
