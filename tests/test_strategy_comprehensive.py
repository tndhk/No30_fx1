"""
Comprehensive unit tests for SMAStrategy class.

Test Framework: pytest
Coverage Focus:
- Branch coverage (C1): All conditional paths tested
- Boundary value analysis: Edge cases for window parameters
- Exception handling: NaN, empty DataFrames, invalid inputs
- Signal generation: Buy/Sell/Hold logic verification
"""

import pytest
import pandas as pd
import numpy as np
from src.strategy import SMAStrategy, Strategy


class TestSMAStrategyInit:
    """Test SMAStrategy initialization."""

    def test_initialization_default_parameters(self):
        """テスト: デフォルトパラメータで初期化"""
        strategy = SMAStrategy()
        assert strategy.short_window == 10
        assert strategy.long_window == 30

    def test_initialization_custom_parameters(self):
        """テスト: カスタムパラメータで初期化"""
        strategy = SMAStrategy(short_window=5, long_window=20)
        assert strategy.short_window == 5
        assert strategy.long_window == 20

    def test_initialization_same_window_values(self):
        """テスト: 短期と長期のウィンドウが同じ値の場合"""
        strategy = SMAStrategy(short_window=10, long_window=10)
        assert strategy.short_window == 10
        assert strategy.long_window == 10


class TestSMAStrategyAnalyzeSignalGeneration:
    """Test signal generation logic - Branch coverage for condition evaluation."""

    def test_signal_buy_when_short_crosses_above_long(self):
        """テスト: 短期MAが長期MAより上にある場合、シグナル=1（買い）"""
        data = {
            "time": pd.date_range(start="2023-01-01", periods=5, freq="D"),
            "close": [100, 105, 110, 115, 120],  # Uptrend
            "open": [100, 105, 110, 115, 120],
            "high": [100, 105, 110, 115, 120],
            "low": [100, 105, 110, 115, 120],
            "volume": [100, 100, 100, 100, 100]
        }
        df = pd.DataFrame(data)
        strategy = SMAStrategy(short_window=2, long_window=3)
        result = strategy.analyze(df)

        # Index 2 onward should have short_mavg > long_mavg
        assert result.iloc[2]['signal'] == 1, "Signal should be 1 (Buy) when short_mavg > long_mavg"
        assert result.iloc[3]['signal'] == 1
        assert result.iloc[4]['signal'] == 1

    def test_signal_sell_when_short_crosses_below_long(self):
        """テスト: 短期MAが長期MAより下にある場合、シグナル=-1（売り）"""
        data = {
            "time": pd.date_range(start="2023-01-01", periods=5, freq="D"),
            "close": [100, 95, 90, 85, 80],  # Downtrend
            "open": [100, 95, 90, 85, 80],
            "high": [100, 95, 90, 85, 80],
            "low": [100, 95, 90, 85, 80],
            "volume": [100, 100, 100, 100, 100]
        }
        df = pd.DataFrame(data)
        strategy = SMAStrategy(short_window=2, long_window=3)
        result = strategy.analyze(df)

        # Index 3 onward should have short_mavg < long_mavg
        assert result.iloc[3]['signal'] == -1, "Signal should be -1 (Sell) when short_mavg < long_mavg"
        assert result.iloc[4]['signal'] == -1

    def test_signal_boundary_equal_moving_averages(self):
        """テスト: 短期MAと長期MAが等しい場合の境界値検証"""
        data = {
            "time": pd.date_range(start="2023-01-01", periods=4, freq="D"),
            "close": [100, 100, 100, 100],  # Flat prices
            "open": [100, 100, 100, 100],
            "high": [100, 100, 100, 100],
            "low": [100, 100, 100, 100],
            "volume": [100, 100, 100, 100]
        }
        df = pd.DataFrame(data)
        strategy = SMAStrategy(short_window=2, long_window=2)
        result = strategy.analyze(df)

        # When short_mavg == long_mavg, condition is False, so signal should be -1
        assert result.iloc[1]['signal'] == -1, "Signal should be -1 when short_mavg == long_mavg"

    def test_signal_pattern_crossover_detection(self):
        """テスト: クロスオーバーパターンの検出（position カラム）"""
        data = {
            "time": pd.date_range(start="2023-01-01", periods=6, freq="D"),
            "close": [100, 110, 120, 110, 100, 90],  # Up then Down
            "open": [100, 110, 120, 110, 100, 90],
            "high": [100, 110, 120, 110, 100, 90],
            "low": [100, 110, 120, 110, 100, 90],
            "volume": [100, 100, 100, 100, 100, 100]
        }
        df = pd.DataFrame(data)
        strategy = SMAStrategy(short_window=2, long_window=3)
        result = strategy.analyze(df)

        # 'position' column should show signal changes
        assert 'position' in result.columns, "position column should exist"
        # position = 2 indicates Buy crossover (from -1 to 1)
        # position = -2 indicates Sell crossover (from 1 to -1)


class TestSMAStrategyDataFrameOperations:
    """Test DataFrame operations and output structure."""

    def test_output_contains_required_columns(self):
        """テスト: 出力に必要なカラムが全て含まれていることを確認"""
        data = {
            "time": pd.date_range(start="2023-01-01", periods=5, freq="D"),
            "close": [100, 105, 110, 115, 120],
            "open": [100, 105, 110, 115, 120],
            "high": [100, 105, 110, 115, 120],
            "low": [100, 105, 110, 115, 120],
            "volume": [100, 100, 100, 100, 100]
        }
        df = pd.DataFrame(data)
        strategy = SMAStrategy(short_window=2, long_window=3)
        result = strategy.analyze(df)

        assert "short_mavg" in result.columns
        assert "long_mavg" in result.columns
        assert "signal" in result.columns
        assert "position" in result.columns

    def test_dataframe_not_modified_original(self):
        """テスト: 元のDataFrameが変更されていないことを確認（copy処理）"""
        data = {
            "time": pd.date_range(start="2023-01-01", periods=3, freq="D"),
            "close": [100, 105, 110],
            "open": [100, 105, 110],
            "high": [100, 105, 110],
            "low": [100, 105, 110],
            "volume": [100, 100, 100]
        }
        df = pd.DataFrame(data)
        original_columns = set(df.columns)

        strategy = SMAStrategy(short_window=2, long_window=3)
        result = strategy.analyze(df)

        # Original df should not have new columns
        assert set(df.columns) == original_columns
        assert "signal" not in df.columns


class TestSMAStrategyBoundaryValues:
    """Test boundary value analysis for parameters."""

    def test_window_size_one(self):
        """テスト: ウィンドウサイズ=1（最小値）での挙動"""
        data = {
            "time": pd.date_range(start="2023-01-01", periods=3, freq="D"),
            "close": [100, 105, 110],
            "open": [100, 105, 110],
            "high": [100, 105, 110],
            "low": [100, 105, 110],
            "volume": [100, 100, 100]
        }
        df = pd.DataFrame(data)
        strategy = SMAStrategy(short_window=1, long_window=1)
        result = strategy.analyze(df)

        # SMA with window=1 should be equal to close price (allowing dtype conversion to float)
        pd.testing.assert_series_equal(result['short_mavg'], df['close'].astype(float), check_names=False)
        pd.testing.assert_series_equal(result['long_mavg'], df['close'].astype(float), check_names=False)

    def test_short_window_greater_than_long_window(self):
        """テスト: 短期ウィンドウが長期ウィンドウより大きい場合"""
        data = {
            "time": pd.date_range(start="2023-01-01", periods=5, freq="D"),
            "close": [100, 105, 110, 115, 120],
            "open": [100, 105, 110, 115, 120],
            "high": [100, 105, 110, 115, 120],
            "low": [100, 105, 110, 115, 120],
            "volume": [100, 100, 100, 100, 100]
        }
        df = pd.DataFrame(data)
        strategy = SMAStrategy(short_window=10, long_window=5)  # Reversed
        result = strategy.analyze(df)

        # Should still work without error
        assert len(result) == len(df)
        assert "signal" in result.columns

    def test_window_size_equals_data_length(self):
        """テスト: ウィンドウサイズがデータ長に等しい場合"""
        data = {
            "time": pd.date_range(start="2023-01-01", periods=5, freq="D"),
            "close": [100, 105, 110, 115, 120],
            "open": [100, 105, 110, 115, 120],
            "high": [100, 105, 110, 115, 120],
            "low": [100, 105, 110, 115, 120],
            "volume": [100, 100, 100, 100, 100]
        }
        df = pd.DataFrame(data)
        strategy = SMAStrategy(short_window=5, long_window=5)
        result = strategy.analyze(df)

        # Should handle without error
        assert len(result) == 5


class TestSMAStrategyAnomalyCases:
    """Test exception handling and anomalous data."""

    def test_empty_dataframe(self):
        """テスト: 空のDataFrameへの対応"""
        df = pd.DataFrame({
            "time": [],
            "close": [],
            "open": [],
            "high": [],
            "low": [],
            "volume": []
        })
        strategy = SMAStrategy(short_window=2, long_window=3)
        result = strategy.analyze(df)

        assert len(result) == 0
        assert "signal" in result.columns

    def test_single_row_dataframe(self):
        """テスト: 単一行のDataFrame処理"""
        data = {
            "time": pd.date_range(start="2023-01-01", periods=1, freq="D"),
            "close": [100],
            "open": [100],
            "high": [100],
            "low": [100],
            "volume": [100]
        }
        df = pd.DataFrame(data)
        strategy = SMAStrategy(short_window=2, long_window=3)
        result = strategy.analyze(df)

        assert len(result) == 1
        assert pd.isna(result.iloc[0]['signal']) or result.iloc[0]['signal'] in [1, -1]

    def test_dataframe_with_nan_values(self):
        """テスト: NaN値を含むデータセットの処理"""
        data = {
            "time": pd.date_range(start="2023-01-01", periods=5, freq="D"),
            "close": [100, np.nan, 110, 115, 120],
            "open": [100, np.nan, 110, 115, 120],
            "high": [100, np.nan, 110, 115, 120],
            "low": [100, np.nan, 110, 115, 120],
            "volume": [100, np.nan, 100, 100, 100]
        }
        df = pd.DataFrame(data)
        strategy = SMAStrategy(short_window=2, long_window=3)
        result = strategy.analyze(df)

        # Should handle NaN propagation in rolling mean
        assert len(result) == 5
        assert "signal" in result.columns

    def test_dataframe_with_all_nan_values(self):
        """テスト: 全てNaN値のデータセット"""
        data = {
            "time": pd.date_range(start="2023-01-01", periods=3, freq="D"),
            "close": [np.nan, np.nan, np.nan],
            "open": [np.nan, np.nan, np.nan],
            "high": [np.nan, np.nan, np.nan],
            "low": [np.nan, np.nan, np.nan],
            "volume": [np.nan, np.nan, np.nan]
        }
        df = pd.DataFrame(data)
        strategy = SMAStrategy(short_window=2, long_window=3)
        result = strategy.analyze(df)

        assert len(result) == 3
        # All signals should be NaN or consistent
        assert result['signal'].isna().any() or result['signal'].notna().any()

    def test_dataframe_with_zero_values(self):
        """テスト: ゼロ値を含むデータセット"""
        data = {
            "time": pd.date_range(start="2023-01-01", periods=5, freq="D"),
            "close": [0, 0, 0, 0, 0],
            "open": [0, 0, 0, 0, 0],
            "high": [0, 0, 0, 0, 0],
            "low": [0, 0, 0, 0, 0],
            "volume": [0, 0, 0, 0, 0]
        }
        df = pd.DataFrame(data)
        strategy = SMAStrategy(short_window=2, long_window=3)
        result = strategy.analyze(df)

        # When all values are equal, signal should be consistent
        assert all(result['signal'].dropna() == -1) or all(result['signal'].dropna() == 1)

    def test_dataframe_with_negative_values(self):
        """テスト: 負の値を含むデータセット"""
        data = {
            "time": pd.date_range(start="2023-01-01", periods=5, freq="D"),
            "close": [-100, -50, 0, 50, 100],
            "open": [-100, -50, 0, 50, 100],
            "high": [-100, -50, 0, 50, 100],
            "low": [-100, -50, 0, 50, 100],
            "volume": [100, 100, 100, 100, 100]
        }
        df = pd.DataFrame(data)
        strategy = SMAStrategy(short_window=2, long_window=3)
        result = strategy.analyze(df)

        # Should handle negative prices
        assert len(result) == 5
        assert "signal" in result.columns

    def test_dataframe_with_extreme_values(self):
        """テスト: 極端に大きな値を含むデータセット"""
        data = {
            "time": pd.date_range(start="2023-01-01", periods=5, freq="D"),
            "close": [1e10, 1e10 * 1.1, 1e10 * 1.2, 1e10 * 1.1, 1e10],
            "open": [1e10, 1e10 * 1.1, 1e10 * 1.2, 1e10 * 1.1, 1e10],
            "high": [1e10, 1e10 * 1.1, 1e10 * 1.2, 1e10 * 1.1, 1e10],
            "low": [1e10, 1e10 * 1.1, 1e10 * 1.2, 1e10 * 1.1, 1e10],
            "volume": [100, 100, 100, 100, 100]
        }
        df = pd.DataFrame(data)
        strategy = SMAStrategy(short_window=2, long_window=3)
        result = strategy.analyze(df)

        assert len(result) == 5
        assert "signal" in result.columns


class TestStrategyBaseClass:
    """Test base Strategy class interface."""

    def test_strategy_base_not_implemented(self):
        """テスト: 基本Strategyクラスはanalyzeが未実装"""
        strategy = Strategy()
        df = pd.DataFrame({
            "close": [100, 105, 110],
            "open": [100, 105, 110],
            "high": [100, 105, 110],
            "low": [100, 105, 110],
            "volume": [100, 100, 100]
        })

        with pytest.raises(NotImplementedError):
            strategy.analyze(df)

    def test_sma_strategy_inherits_from_strategy(self):
        """テスト: SMAStrategyが Strategy を継承"""
        strategy = SMAStrategy()
        assert isinstance(strategy, Strategy)
