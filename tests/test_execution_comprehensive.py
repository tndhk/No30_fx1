"""
Comprehensive unit tests for OrderExecutor class.

Test Framework: pytest
Coverage Focus:
- Branch coverage (C1): All conditional paths (mock vs real, client presence)
- Boundary value analysis: Edge cases for units parameter
- Exception handling: Invalid inputs, None values
- Return value verification: Mock and real execution responses
"""

import pytest
from unittest.mock import MagicMock, patch
from src.execution import OrderExecutor
from src.config import Config


class TestOrderExecutorInit:
    """Test OrderExecutor initialization."""

    def test_initialization_with_client(self):
        """テスト: クライアント指定での初期化"""
        mock_client = MagicMock()
        executor = OrderExecutor(client=mock_client)

        assert executor.client is mock_client

    def test_initialization_without_client(self):
        """テスト: クライアントなしでの初期化"""
        executor = OrderExecutor(client=None)

        assert executor.client is None

    def test_initialization_default_none_client(self):
        """テスト: デフォルトではクライアント=None"""
        executor = OrderExecutor()

        assert executor.client is None

    def test_env_set_from_config(self):
        """テスト: 環境情報がConfigから取得される"""
        with patch("src.execution.Config.ENV", "mock"):
            executor = OrderExecutor()
            assert executor.env == "mock"


class TestOrderExecutorMockExecution:
    """Test mock mode execution - Branch coverage for env=='mock'."""

    @patch("src.execution.Config.ENV", "mock")
    def test_mock_execution_basic_order(self, capsys):
        """テスト: Mock モードでの基本注文実行"""
        executor = OrderExecutor()
        result = executor.execute_order("USD_JPY", units=1000)

        assert result is not None
        assert result["id"] == "mock_order_id"
        assert result["instrument"] == "USD_JPY"
        assert result["units"] == 1000

    @patch("src.execution.Config.ENV", "mock")
    def test_mock_execution_with_stop_loss(self, capsys):
        """テスト: Mock モードでのStop Loss指定"""
        executor = OrderExecutor()
        result = executor.execute_order(
            "EUR_USD",
            units=500,
            stop_loss=1.0500,
            take_profit=1.0600
        )

        assert result["instrument"] == "EUR_USD"
        assert result["units"] == 500
        # Verify the output message
        captured = capsys.readouterr()
        assert "MOCK EXECUTION" in captured.out
        assert "SL: 1.05" in captured.out
        assert "TP: 1.06" in captured.out

    @patch("src.execution.Config.ENV", "mock")
    def test_mock_execution_negative_units(self, capsys):
        """テスト: Mock モードでの負の units（売り注文）"""
        executor = OrderExecutor()
        result = executor.execute_order("GBP_USD", units=-2000)

        assert result["units"] == -2000
        captured = capsys.readouterr()
        assert "Units: -2000" in captured.out

    @patch("src.execution.Config.ENV", "mock")
    def test_mock_execution_zero_units(self, capsys):
        """テスト: Mock モードでの units=0（境界値）"""
        executor = OrderExecutor()
        result = executor.execute_order("AUD_USD", units=0)

        assert result["units"] == 0
        captured = capsys.readouterr()
        assert "Units: 0" in captured.out

    @patch("src.execution.Config.ENV", "mock")
    def test_mock_execution_large_units(self, capsys):
        """テスト: Mock モードでの大きな units 値"""
        executor = OrderExecutor()
        result = executor.execute_order("USD_CAD", units=1000000)

        assert result["units"] == 1000000


class TestOrderExecutorClientNoneExecution:
    """Test execution when client is None - Branch coverage for client is None."""

    def test_client_none_triggers_mock_mode(self, capsys):
        """テスト: client=None の場合は Mock モードで実行"""
        with patch("src.execution.Config.ENV", "live"):
            # Even though ENV is 'live', client=None should trigger mock mode
            executor = OrderExecutor(client=None)
            result = executor.execute_order("USD_JPY", units=1000)

            assert result["id"] == "mock_order_id"
            captured = capsys.readouterr()
            assert "MOCK EXECUTION" in captured.out

    def test_client_none_with_all_parameters(self, capsys):
        """テスト: client=None で全パラメータを指定"""
        executor = OrderExecutor(client=None)
        result = executor.execute_order(
            "EUR_GBP",
            units=5000,
            stop_loss=0.8500,
            take_profit=0.8700
        )

        assert result["instrument"] == "EUR_GBP"
        assert result["units"] == 5000


class TestOrderExecutorRealExecution:
    """Test real mode execution (non-implemented) - Branch coverage for real mode."""

    def test_real_execution_not_implemented(self, capsys):
        """テスト: 本番モード実行は未実装（安全のため）"""
        mock_client = MagicMock()

        with patch("src.execution.Config.ENV", "live"):
            executor = OrderExecutor(client=mock_client)
            result = executor.execute_order("USD_JPY", units=1000)

            # Real execution returns empty dict in current implementation
            assert result == {}
            captured = capsys.readouterr()
            assert "REAL EXECUTION" in captured.out
            assert "Not implemented" in captured.out

    def test_real_execution_with_client_present(self, capsys):
        """テスト: クライアント有のreal モード"""
        mock_client = MagicMock()

        with patch("src.execution.Config.ENV", "live"):
            executor = OrderExecutor(client=mock_client)
            result = executor.execute_order("EUR_USD", units=2000)

            assert result == {}

    def test_real_execution_practice_mode(self, capsys):
        """テスト: practice モードでの実行"""
        mock_client = MagicMock()

        with patch("src.execution.Config.ENV", "practice"):
            executor = OrderExecutor(client=mock_client)
            result = executor.execute_order("GBP_USD", units=1500)

            # practice mode != mock, so it should go to real execution path
            assert result == {}


class TestOrderExecutorEdgeCases:
    """Test edge cases and boundary conditions."""

    @patch("src.execution.Config.ENV", "mock")
    def test_none_instrument_parameter(self):
        """テスト: instrument=None での実行"""
        executor = OrderExecutor()
        result = executor.execute_order(None, units=1000)

        assert result["instrument"] is None
        assert result["units"] == 1000

    @patch("src.execution.Config.ENV", "mock")
    def test_empty_string_instrument(self):
        """テスト: instrument='' での実行"""
        executor = OrderExecutor()
        result = executor.execute_order("", units=500)

        assert result["instrument"] == ""
        assert result["units"] == 500

    @patch("src.execution.Config.ENV", "mock")
    def test_none_stop_loss_take_profit(self, capsys):
        """テスト: stop_loss=None, take_profit=None での実行"""
        executor = OrderExecutor()
        result = executor.execute_order("USD_JPY", units=1000, stop_loss=None, take_profit=None)

        assert result["units"] == 1000
        captured = capsys.readouterr()
        assert "SL: None" in captured.out
        assert "TP: None" in captured.out

    @patch("src.execution.Config.ENV", "mock")
    def test_decimal_units_value(self):
        """テスト: units が float 型の場合"""
        executor = OrderExecutor()
        # Some APIs might accept fractional units
        result = executor.execute_order("USD_JPY", units=1500.5)

        assert result["units"] == 1500.5

    @patch("src.execution.Config.ENV", "mock")
    def test_very_large_stop_loss_take_profit(self, capsys):
        """テスト: 極端に大きな Stop Loss/Take Profit値"""
        executor = OrderExecutor()
        result = executor.execute_order(
            "USD_JPY",
            units=1000,
            stop_loss=1e10,
            take_profit=2e10
        )

        assert result["units"] == 1000
        captured = capsys.readouterr()
        assert "USD_JPY" in captured.out


class TestOrderExecutorMultipleOrders:
    """Test consecutive order executions."""

    @patch("src.execution.Config.ENV", "mock")
    def test_multiple_orders_sequential_execution(self):
        """テスト: 複数注文の順序実行"""
        executor = OrderExecutor()

        result1 = executor.execute_order("USD_JPY", units=1000)
        result2 = executor.execute_order("EUR_USD", units=500)
        result3 = executor.execute_order("GBP_USD", units=-1000)

        assert result1["instrument"] == "USD_JPY"
        assert result2["instrument"] == "EUR_USD"
        assert result3["instrument"] == "GBP_USD"

    @patch("src.execution.Config.ENV", "mock")
    def test_executor_state_persistence(self):
        """テスト: Executor インスタンスの状態保持"""
        executor = OrderExecutor()
        executor.custom_attr = "test_value"

        result = executor.execute_order("USD_JPY", units=1000)

        # Verify executor state is preserved
        assert executor.custom_attr == "test_value"
        assert result["units"] == 1000


class TestOrderExecutorIntegration:
    """Integration-like tests for realistic scenarios."""

    @patch("src.execution.Config.ENV", "mock")
    def test_grid_trading_scenario(self):
        """テスト: グリッドトレードシナリオ"""
        executor = OrderExecutor()
        prices = [100, 101, 102, 101, 100]
        units_per_level = 100

        orders = []
        for price in prices:
            result = executor.execute_order("USD_JPY", units=units_per_level)
            orders.append(result)

        assert len(orders) == 5
        assert all(order["units"] == units_per_level for order in orders)

    @patch("src.execution.Config.ENV", "mock")
    def test_position_reversal_scenario(self):
        """テスト: ポジション反転シナリオ"""
        executor = OrderExecutor()

        # Buy 1000 units
        buy_result = executor.execute_order("EUR_USD", units=1000)
        assert buy_result["units"] == 1000

        # Sell 1000 units (close position)
        sell_result = executor.execute_order("EUR_USD", units=-1000)
        assert sell_result["units"] == -1000

    @patch("src.execution.Config.ENV", "mock")
    def test_stop_loss_take_profit_realistic(self):
        """テスト: 現実的な SL/TP 値での実行"""
        executor = OrderExecutor()

        result = executor.execute_order(
            "EUR_USD",
            units=100000,
            stop_loss=1.0800,  # -200 pips
            take_profit=1.1200  # +400 pips
        )

        assert result["units"] == 100000
        assert result["id"] == "mock_order_id"


class TestOrderExecutorEnvHandling:
    """Test different environment configurations."""

    def test_env_fallback_to_mock_when_not_live_or_practice(self, capsys):
        """テスト: ENV が 'mock' でも 'live'/'practice' でもない場合"""
        mock_client = MagicMock()

        with patch("src.execution.Config.ENV", "development"):
            executor = OrderExecutor(client=mock_client)
            result = executor.execute_order("USD_JPY", units=1000)

            # Should go to real execution (not mock)
            assert result == {}

    @patch("src.execution.Config.ENV", "mock")
    def test_mock_env_with_client_present(self):
        """テスト: env='mock' かつ client が存在する場合"""
        mock_client = MagicMock()
        executor = OrderExecutor(client=mock_client)

        result = executor.execute_order("USD_JPY", units=1000)

        # env='mock' takes precedence
        assert result["id"] == "mock_order_id"
        assert result["instrument"] == "USD_JPY"

    def test_env_none_handling(self):
        """テスト: ENV が None の場合"""
        with patch("src.execution.Config.ENV", None):
            executor = OrderExecutor()
            # ENV = None should not equal 'mock', but client is None
            # so the condition (self.env == "mock" or self.client is None) is True
            result = executor.execute_order("USD_JPY", units=1000)

            # When client is None, mock execution is triggered
            assert result["id"] == "mock_order_id"
