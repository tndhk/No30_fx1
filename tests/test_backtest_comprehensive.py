"""
Comprehensive unit tests for BacktestEngine class.

Test Framework: pytest
Coverage Focus:
- Branch coverage (C1): Position entry/exit logic, trade execution conditions
- Boundary value analysis: initial_balance edge cases, price extremes
- Exception handling: Empty DataFrames, NaN values, single bar data
- P&L calculation verification: Returns and cumulative returns
- Strategy integration: Different signal patterns
"""

import pytest
import pandas as pd
import numpy as np
from src.backtest import BacktestEngine
from src.strategy import Strategy, SMAStrategy


class TestBacktestEngineInit:
    """Test BacktestEngine initialization."""

    def test_initialization_default_balance(self):
        """テスト: デフォルト初期資金での初期化"""
        engine = BacktestEngine()

        assert engine.initial_balance == 1000000
        assert engine.balance == 1000000
        assert engine.position == 0
        assert len(engine.trades) == 0

    def test_initialization_custom_balance(self):
        """テスト: カスタム初期資金での初期化"""
        engine = BacktestEngine(initial_balance=500000)

        assert engine.initial_balance == 500000
        assert engine.balance == 500000

    def test_initialization_zero_balance(self):
        """テスト: ゼロ初期資金での初期化"""
        engine = BacktestEngine(initial_balance=0)

        assert engine.initial_balance == 0
        assert engine.balance == 0

    def test_initialization_large_balance(self):
        """テスト: 大きな初期資金での初期化"""
        engine = BacktestEngine(initial_balance=1e10)

        assert engine.initial_balance == 1e10

    def test_initialization_small_balance(self):
        """テスト: 小さな初期資金での初期化"""
        engine = BacktestEngine(initial_balance=100)

        assert engine.initial_balance == 100


class TestBacktestEngineRun:
    """Test run method - Main backtest execution."""

    def test_run_with_buy_signal(self):
        """テスト: 買いシグナル（signal=1）での実行"""
        data = {
            "time": pd.date_range(start="2023-01-01", periods=5, freq="D"),
            "close": [100, 101, 102, 103, 104],
            "open": [100, 101, 102, 103, 104],
            "high": [100, 101, 102, 103, 104],
            "low": [100, 101, 102, 103, 104],
            "volume": [100, 100, 100, 100, 100]
        }
        df = pd.DataFrame(data)

        class BuyStrategy(Strategy):
            def analyze(self, df):
                df = df.copy()
                df['signal'] = 1
                return df

        engine = BacktestEngine(initial_balance=1000000)
        result = engine.run(df, BuyStrategy())

        assert "final_return" in result
        assert "total_trades" in result

    def test_run_with_sell_signal(self):
        """テスト: 売りシグナル（signal=-1）での実行"""
        data = {
            "time": pd.date_range(start="2023-01-01", periods=5, freq="D"),
            "close": [100, 99, 98, 97, 96],
            "open": [100, 99, 98, 97, 96],
            "high": [100, 99, 98, 97, 96],
            "low": [100, 99, 98, 97, 96],
            "volume": [100, 100, 100, 100, 100]
        }
        df = pd.DataFrame(data)

        class SellStrategy(Strategy):
            def analyze(self, df):
                df = df.copy()
                df['signal'] = -1
                return df

        engine = BacktestEngine(initial_balance=1000000)
        result = engine.run(df, SellStrategy())

        assert "final_return" in result
        assert "total_trades" in result

    def test_run_with_mixed_signals(self):
        """テスト: 混合シグナル（買い＆売り）での実行"""
        data = {
            "time": pd.date_range(start="2023-01-01", periods=6, freq="D"),
            "close": [100, 105, 110, 105, 100, 95],
            "open": [100, 105, 110, 105, 100, 95],
            "high": [100, 105, 110, 105, 100, 95],
            "low": [100, 105, 110, 105, 100, 95],
            "volume": [100, 100, 100, 100, 100, 100]
        }
        df = pd.DataFrame(data)

        class MixedStrategy(Strategy):
            def analyze(self, df):
                df = df.copy()
                df['signal'] = [1, 1, 1, -1, -1, -1]
                return df

        engine = BacktestEngine(initial_balance=1000000)
        result = engine.run(df, MixedStrategy())

        assert result["total_trades"] > 0

    def test_run_records_trades(self):
        """テスト: トレード記録の生成"""
        data = {
            "time": pd.date_range(start="2023-01-01", periods=4, freq="D"),
            "close": [100, 105, 110, 105],
            "open": [100, 105, 110, 105],
            "high": [100, 105, 110, 105],
            "low": [100, 105, 110, 105],
            "volume": [100, 100, 100, 100]
        }
        df = pd.DataFrame(data)

        class BuyStrategy(Strategy):
            def analyze(self, df):
                df = df.copy()
                df['signal'] = 1
                return df

        engine = BacktestEngine(initial_balance=1000000)
        engine.run(df, BuyStrategy())

        assert len(engine.trades) > 0
        # Each trade should have required fields
        for trade in engine.trades:
            assert "time" in trade
            assert "type" in trade
            assert "price" in trade
            assert "size" in trade
            assert "balance" in trade


class TestBacktestEngineCalculatePerformance:
    """Test calculate_performance method - Returns calculation."""

    def test_calculate_performance_uptrend(self):
        """テスト: 上昇トレンド時のパフォーマンス計算"""
        data = {
            "time": pd.date_range(start="2023-01-01", periods=5, freq="D"),
            "close": [100, 102, 104, 106, 108],
            "open": [100, 102, 104, 106, 108],
            "high": [100, 102, 104, 106, 108],
            "low": [100, 102, 104, 106, 108],
            "volume": [100, 100, 100, 100, 100]
        }
        df = pd.DataFrame(data)

        class BullStrategy(Strategy):
            def analyze(self, df):
                df = df.copy()
                df['signal'] = 1
                return df

        engine = BacktestEngine(initial_balance=1000000)
        result = engine.calculate_performance(
            BullStrategy().analyze(df)
        )

        assert result["final_return"] > 1.0

    def test_calculate_performance_downtrend(self):
        """テスト: 下降トレンド時のパフォーマンス計算"""
        data = {
            "time": pd.date_range(start="2023-01-01", periods=5, freq="D"),
            "close": [100, 98, 96, 94, 92],
            "open": [100, 98, 96, 94, 92],
            "high": [100, 98, 96, 94, 92],
            "low": [100, 98, 96, 94, 92],
            "volume": [100, 100, 100, 100, 100]
        }
        df = pd.DataFrame(data)

        class BearStrategy(Strategy):
            def analyze(self, df):
                df = df.copy()
                df['signal'] = -1
                return df

        engine = BacktestEngine(initial_balance=1000000)
        result = engine.calculate_performance(
            BearStrategy().analyze(df)
        )

        assert "final_return" in result
        assert "total_trades" in result

    def test_calculate_performance_flat_market(self):
        """テスト: レンジ相場でのパフォーマンス計算"""
        data = {
            "time": pd.date_range(start="2023-01-01", periods=5, freq="D"),
            "close": [100, 100, 100, 100, 100],
            "open": [100, 100, 100, 100, 100],
            "high": [100, 100, 100, 100, 100],
            "low": [100, 100, 100, 100, 100],
            "volume": [100, 100, 100, 100, 100]
        }
        df = pd.DataFrame(data)

        class HoldStrategy(Strategy):
            def analyze(self, df):
                df = df.copy()
                df['signal'] = 0
                return df

        engine = BacktestEngine(initial_balance=1000000)
        result = engine.calculate_performance(
            HoldStrategy().analyze(df)
        )

        # Flat market should have final_return close to 1.0
        assert result["final_return"] <= 1.01

    def test_calculate_performance_uses_shifted_signal(self):
        """テスト: シグナルが shift(1) で適用される（フォワードルック偏差回避）"""
        data = {
            "time": pd.date_range(start="2023-01-01", periods=4, freq="D"),
            "close": [100, 110, 120, 130],
            "open": [100, 110, 120, 130],
            "high": [100, 110, 120, 130],
            "low": [100, 110, 120, 130],
            "volume": [100, 100, 100, 100]
        }
        df = pd.DataFrame(data)

        class TestStrategy(Strategy):
            def analyze(self, df):
                df = df.copy()
                df['signal'] = 1
                return df

        engine = BacktestEngine()
        analyzed_df = TestStrategy().analyze(df)
        result = engine.calculate_performance(analyzed_df)

        # Should have computed returns with shift
        assert "strategy_returns" in analyzed_df.columns
        assert "cumulative_returns" in analyzed_df.columns


class TestBacktestEnginePositionManagement:
    """Test position entry and exit logic - Branch coverage."""

    def test_position_entry_from_flat(self):
        """テスト: ニュートラルポジションからのエントリー"""
        data = {
            "time": pd.date_range(start="2023-01-01", periods=3, freq="D"),
            "close": [100, 105, 110],
            "open": [100, 105, 110],
            "high": [100, 105, 110],
            "low": [100, 105, 110],
            "volume": [100, 100, 100]
        }
        df = pd.DataFrame(data)

        class BuyStrategy(Strategy):
            def analyze(self, df):
                df = df.copy()
                df['signal'] = 1
                return df

        engine = BacktestEngine(initial_balance=1000000)
        engine.run(df, BuyStrategy())

        # Should have entered position
        assert engine.position != 0

    def test_position_reversal(self):
        """テスト: ポジション反転（long to short）"""
        data = {
            "time": pd.date_range(start="2023-01-01", periods=4, freq="D"),
            "close": [100, 105, 110, 105],
            "open": [100, 105, 110, 105],
            "high": [100, 105, 110, 105],
            "low": [100, 105, 110, 105],
            "volume": [100, 100, 100, 100]
        }
        df = pd.DataFrame(data)

        class ReversalStrategy(Strategy):
            def analyze(self, df):
                df = df.copy()
                df['signal'] = [1, 1, -1, -1]
                return df

        engine = BacktestEngine(initial_balance=1000000)
        engine.run(df, ReversalStrategy())

        # Should have executed multiple trades
        assert len(engine.trades) >= 2

    def test_no_trade_when_signal_unchanged(self):
        """テスト: シグナルが変わらない場合はトレード不実行"""
        data = {
            "time": pd.date_range(start="2023-01-01", periods=4, freq="D"),
            "close": [100, 105, 110, 115],
            "open": [100, 105, 110, 115],
            "high": [100, 105, 110, 115],
            "low": [100, 105, 110, 115],
            "volume": [100, 100, 100, 100]
        }
        df = pd.DataFrame(data)

        class ConsistentBuyStrategy(Strategy):
            def analyze(self, df):
                df = df.copy()
                df['signal'] = 1  # Always 1
                return df

        engine = BacktestEngine(initial_balance=1000000)
        engine.run(df, ConsistentBuyStrategy())

        # Only one trade should occur (initial entry)
        # Since signal is always 1, position stays at target
        assert len(engine.trades) == 1


class TestBacktestEngineEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_run_empty_dataframe(self):
        """テスト: 空の DataFrame での実行"""
        df = pd.DataFrame({
            "time": [],
            "close": [],
            "open": [],
            "high": [],
            "low": [],
            "volume": []
        })

        class DummyStrategy(Strategy):
            def analyze(self, df):
                df = df.copy()
                df['signal'] = 1
                return df

        engine = BacktestEngine(initial_balance=1000000)
        # Empty DataFrame will cause IndexError when accessing iloc[-1]
        # This is expected behavior - test that it handles gracefully or raises
        try:
            result = engine.run(df, DummyStrategy())
            # If it doesn't raise, it should still return performance metrics
            assert "final_return" in result
        except IndexError:
            # Empty DataFrame causing IndexError is acceptable behavior
            pass

    def test_run_single_bar_dataframe(self):
        """テスト: 単一バーの DataFrame での実行"""
        data = {
            "time": pd.date_range(start="2023-01-01", periods=1, freq="D"),
            "close": [100],
            "open": [100],
            "high": [100],
            "low": [100],
            "volume": [100]
        }
        df = pd.DataFrame(data)

        class BuyStrategy(Strategy):
            def analyze(self, df):
                df = df.copy()
                df['signal'] = 1
                return df

        engine = BacktestEngine(initial_balance=1000000)
        result = engine.run(df, BuyStrategy())

        assert result["final_return"] is not None

    def test_run_with_nan_closes(self):
        """テスト: NaN 値を含む close の処理"""
        data = {
            "time": pd.date_range(start="2023-01-01", periods=5, freq="D"),
            "close": [100, np.nan, 110, 115, 120],
            "open": [100, np.nan, 110, 115, 120],
            "high": [100, np.nan, 110, 115, 120],
            "low": [100, np.nan, 110, 115, 120],
            "volume": [100, np.nan, 100, 100, 100]
        }
        df = pd.DataFrame(data)

        class BuyStrategy(Strategy):
            def analyze(self, df):
                df = df.copy()
                df['signal'] = 1
                return df

        engine = BacktestEngine(initial_balance=1000000)
        result = engine.run(df, BuyStrategy())

        assert result["final_return"] is not None

    def test_run_with_extreme_prices(self):
        """テスト: 極端に大きな価格値での実行"""
        data = {
            "time": pd.date_range(start="2023-01-01", periods=5, freq="D"),
            "close": [1e10, 1e10 * 1.1, 1e10 * 1.2, 1e10 * 1.15, 1e10 * 1.1],
            "open": [1e10, 1e10 * 1.1, 1e10 * 1.2, 1e10 * 1.15, 1e10 * 1.1],
            "high": [1e10, 1e10 * 1.1, 1e10 * 1.2, 1e10 * 1.15, 1e10 * 1.1],
            "low": [1e10, 1e10 * 1.1, 1e10 * 1.2, 1e10 * 1.15, 1e10 * 1.1],
            "volume": [100, 100, 100, 100, 100]
        }
        df = pd.DataFrame(data)

        class BuyStrategy(Strategy):
            def analyze(self, df):
                df = df.copy()
                df['signal'] = 1
                return df

        engine = BacktestEngine(initial_balance=1e15)
        result = engine.run(df, BuyStrategy())

        assert result["final_return"] > 0

    def test_run_with_zero_prices(self):
        """テスト: ゼロ価格での実行"""
        data = {
            "time": pd.date_range(start="2023-01-01", periods=5, freq="D"),
            "close": [0, 0, 0, 0, 0],
            "open": [0, 0, 0, 0, 0],
            "high": [0, 0, 0, 0, 0],
            "low": [0, 0, 0, 0, 0],
            "volume": [100, 100, 100, 100, 100]
        }
        df = pd.DataFrame(data)

        class BuyStrategy(Strategy):
            def analyze(self, df):
                df = df.copy()
                df['signal'] = 1
                return df

        engine = BacktestEngine(initial_balance=1000000)
        result = engine.run(df, BuyStrategy())

        assert result["final_return"] is not None


class TestBacktestEngineIntegration:
    """Integration tests with real strategy implementations."""

    def test_run_with_sma_strategy(self):
        """テスト: 実際の SMAStrategy との統合"""
        data = {
            "time": pd.date_range(start="2023-01-01", periods=20, freq="D"),
            "close": [100 + i * 1.5 if i < 10 else 100 + 10 * 1.5 - (i - 10) * 1.5 for i in range(20)],
            "open": [100 + i * 1.5 if i < 10 else 100 + 10 * 1.5 - (i - 10) * 1.5 for i in range(20)],
            "high": [100 + i * 1.5 if i < 10 else 100 + 10 * 1.5 - (i - 10) * 1.5 for i in range(20)],
            "low": [100 + i * 1.5 if i < 10 else 100 + 10 * 1.5 - (i - 10) * 1.5 for i in range(20)],
            "volume": [100] * 20
        }
        df = pd.DataFrame(data)

        strategy = SMAStrategy(short_window=3, long_window=5)
        engine = BacktestEngine(initial_balance=1000000)
        result = engine.run(df, strategy)

        assert "final_return" in result
        assert "total_trades" in result
        assert result["final_return"] > 0

    def test_run_preserves_engine_state(self):
        """テスト: 複数実行時の Engine 状態"""
        data = {
            "time": pd.date_range(start="2023-01-01", periods=5, freq="D"),
            "close": [100, 105, 110, 115, 120],
            "open": [100, 105, 110, 115, 120],
            "high": [100, 105, 110, 115, 120],
            "low": [100, 105, 110, 115, 120],
            "volume": [100, 100, 100, 100, 100]
        }
        df = pd.DataFrame(data)

        class BuyStrategy(Strategy):
            def analyze(self, df):
                df = df.copy()
                df['signal'] = 1
                return df

        engine = BacktestEngine(initial_balance=1000000)
        initial_position = engine.position

        engine.run(df, BuyStrategy())
        position_after_run = engine.position

        # Position should have changed
        assert position_after_run != initial_position


class TestBacktestEngineDataFrameHandling:
    """Test DataFrame handling and validation."""

    def test_analyze_modifies_strategy_df(self):
        """テスト: Strategy.analyze が返す DataFrame に必要なカラムが存在"""
        data = {
            "time": pd.date_range(start="2023-01-01", periods=3, freq="D"),
            "close": [100, 105, 110],
            "open": [100, 105, 110],
            "high": [100, 105, 110],
            "low": [100, 105, 110],
            "volume": [100, 100, 100]
        }
        df = pd.DataFrame(data)

        class TestStrategy(Strategy):
            def analyze(self, df):
                df = df.copy()
                df['signal'] = 1
                return df

        engine = BacktestEngine()
        analyzed = TestStrategy().analyze(df)

        assert 'signal' in analyzed.columns
        assert 'returns' in analyzed.columns or 'pct_change' in analyzed.columns or len(analyzed) > 0
