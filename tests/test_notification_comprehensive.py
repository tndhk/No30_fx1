"""
Comprehensive unit tests for Notifier class.

Test Framework: pytest
Coverage Focus:
- Branch coverage (C1): webhook_url presence detection
- Exception handling: API errors, network failures, malformed responses
- Fallback mechanism: Error recovery and stdout fallback
- Message formatting: Trade log formatting verification
- Mock/Stub: requests.post mocking
"""

import pytest
from unittest.mock import MagicMock, patch, call
import requests
from src.notification import Notifier


class TestNotifierInit:
    """Test Notifier initialization."""

    def test_initialization_with_webhook_url(self):
        """テスト: Webhook URL指定での初期化"""
        webhook_url = "https://discord.com/api/webhooks/123/abc"
        notifier = Notifier(webhook_url=webhook_url)

        assert notifier.webhook_url == webhook_url

    def test_initialization_from_environment_variable(self):
        """テスト: 環境変数から Webhook URL を取得"""
        with patch.dict("os.environ", {"DISCORD_WEBHOOK_URL": "https://test.webhook"}):
            notifier = Notifier()
            assert notifier.webhook_url == "https://test.webhook"

    def test_initialization_priority_explicit_over_env(self):
        """テスト: 明示的な Webhook URL が環境変数より優先される"""
        explicit_url = "https://explicit.webhook"
        with patch.dict("os.environ", {"DISCORD_WEBHOOK_URL": "https://env.webhook"}):
            notifier = Notifier(webhook_url=explicit_url)
            assert notifier.webhook_url == explicit_url

    def test_initialization_without_webhook_url(self):
        """テスト: Webhook URL なしでの初期化"""
        with patch.dict("os.environ", {}, clear=True):
            notifier = Notifier()
            assert notifier.webhook_url is None


class TestNotifierSendMessageWithWebhook:
    """Test send_message with webhook URL - Branch coverage for webhook_url presence."""

    @patch("src.notification.requests.post")
    def test_send_message_success(self, mock_post):
        """テスト: メッセージ送信成功"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        notifier = Notifier(webhook_url="https://discord.webhook")
        notifier.send_message("Test message")

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "https://discord.webhook"
        assert kwargs["json"] == {"content": "Test message"}

    @patch("src.notification.requests.post")
    def test_send_message_with_special_characters(self, mock_post):
        """テスト: 特殊文字を含むメッセージ送信"""
        mock_response = MagicMock()
        mock_post.return_value = mock_response

        notifier = Notifier(webhook_url="https://discord.webhook")
        message = "Test 🚀 $100 **bold** _italic_"
        notifier.send_message(message)

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs["json"] == {"content": message}

    @patch("src.notification.requests.post")
    def test_send_message_with_newlines(self, mock_post):
        """テスト: 改行を含むメッセージ"""
        mock_response = MagicMock()
        mock_post.return_value = mock_response

        notifier = Notifier(webhook_url="https://discord.webhook")
        message = "Line 1\nLine 2\nLine 3"
        notifier.send_message(message)

        args, kwargs = mock_post.call_args
        assert kwargs["json"]["content"] == message

    @patch("src.notification.requests.post")
    def test_send_message_with_long_content(self, mock_post):
        """テスト: 長いメッセージ送信"""
        mock_response = MagicMock()
        mock_post.return_value = mock_response

        notifier = Notifier(webhook_url="https://discord.webhook")
        message = "x" * 1000
        notifier.send_message(message)

        mock_post.assert_called_once()

    @patch("src.notification.requests.post")
    def test_send_message_status_code_202(self, mock_post):
        """テスト: ステータスコード 202 (非同期処理受け入れ)"""
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_post.return_value = mock_response

        notifier = Notifier(webhook_url="https://discord.webhook")
        notifier.send_message("Async message")

        mock_post.assert_called_once()


class TestNotifierHttpExceptions:
    """Test HTTP-related exceptions - Exception handling & fallback."""

    @patch("src.notification.requests.post")
    def test_send_message_http_error_404(self, mock_post, capsys):
        """テスト: HTTP 404 エラーの処理"""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_post.return_value = mock_response

        notifier = Notifier(webhook_url="https://discord.webhook")
        notifier.send_message("Test message")

        # Should fallback to stdout
        captured = capsys.readouterr()
        assert "NOTIFICATION ERROR" in captured.out
        assert "NOTIFICATION FALLBACK" in captured.out
        assert "Test message" in captured.out

    @patch("src.notification.requests.post")
    def test_send_message_http_error_500(self, mock_post, capsys):
        """テスト: HTTP 500 エラーの処理"""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")
        mock_post.return_value = mock_response

        notifier = Notifier(webhook_url="https://discord.webhook")
        notifier.send_message("Server error message")

        captured = capsys.readouterr()
        assert "NOTIFICATION ERROR" in captured.out
        assert "Failed to send to Discord" in captured.out

    @patch("src.notification.requests.post")
    def test_send_message_connection_error(self, mock_post, capsys):
        """テスト: 接続エラーの処理"""
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")

        notifier = Notifier(webhook_url="https://discord.webhook")
        notifier.send_message("Connection test")

        captured = capsys.readouterr()
        assert "NOTIFICATION ERROR" in captured.out
        assert "Connection failed" in captured.out
        assert "NOTIFICATION FALLBACK" in captured.out

    @patch("src.notification.requests.post")
    def test_send_message_timeout_error(self, mock_post, capsys):
        """テスト: タイムアウトエラーの処理"""
        mock_post.side_effect = requests.exceptions.Timeout("Request timeout")

        notifier = Notifier(webhook_url="https://discord.webhook")
        notifier.send_message("Timeout message")

        captured = capsys.readouterr()
        assert "NOTIFICATION ERROR" in captured.out
        assert "NOTIFICATION FALLBACK" in captured.out

    @patch("src.notification.requests.post")
    def test_send_message_request_exception(self, mock_post, capsys):
        """テスト: 汎用 RequestException の処理"""
        mock_post.side_effect = requests.exceptions.RequestException("General error")

        notifier = Notifier(webhook_url="https://discord.webhook")
        notifier.send_message("General error message")

        captured = capsys.readouterr()
        assert "NOTIFICATION ERROR" in captured.out

    @patch("src.notification.requests.post")
    def test_send_message_generic_exception(self, mock_post, capsys):
        """テスト: 例外ハンドリング（汎用Exception）"""
        mock_post.side_effect = Exception("Unexpected error")

        notifier = Notifier(webhook_url="https://discord.webhook")
        notifier.send_message("Unexpected error message")

        captured = capsys.readouterr()
        assert "NOTIFICATION ERROR" in captured.out
        assert "Unexpected error" in captured.out


class TestNotifierNoWebhook:
    """Test send_message without webhook URL - Branch coverage for no webhook."""

    def test_send_message_without_webhook_stdout(self, capsys):
        """テスト: Webhook URL なしで stdout に出力"""
        notifier = Notifier(webhook_url=None)
        notifier.send_message("Test message")

        captured = capsys.readouterr()
        assert "NOTIFICATION (STDOUT)" in captured.out
        assert "Test message" in captured.out

    def test_send_message_without_webhook_empty_env(self, capsys):
        """テスト: 環境変数が空の場合も stdout に出力"""
        with patch.dict("os.environ", {}, clear=True):
            notifier = Notifier()
            notifier.send_message("Empty env message")

            captured = capsys.readouterr()
            assert "NOTIFICATION (STDOUT)" in captured.out

    def test_send_message_special_chars_stdout(self, capsys):
        """テスト: stdout での特殊文字出力"""
        notifier = Notifier(webhook_url=None)
        message = "Special chars: 🚀 **bold** _italic_"
        notifier.send_message(message)

        captured = capsys.readouterr()
        assert "Special chars: 🚀 **bold** _italic_" in captured.out

    def test_send_message_multiline_stdout(self, capsys):
        """テスト: stdout での複数行出力"""
        notifier = Notifier(webhook_url=None)
        message = "Line 1\nLine 2\nLine 3"
        notifier.send_message(message)

        captured = capsys.readouterr()
        assert "Line 1\nLine 2\nLine 3" in captured.out


class TestNotifierSendTradeLog:
    """Test send_trade_log method."""

    @patch("src.notification.requests.post")
    def test_send_trade_log_basic(self, mock_post):
        """テスト: 基本的なトレードログ送信"""
        mock_response = MagicMock()
        mock_post.return_value = mock_response

        notifier = Notifier(webhook_url="https://discord.webhook")
        trade_details = {
            "instrument": "USD_JPY",
            "units": 1000,
            "id": "order_123"
        }
        notifier.send_trade_log(trade_details)

        # Verify the message format
        args, kwargs = mock_post.call_args
        message = kwargs["json"]["content"]
        assert "Trade Executed" in message
        assert "USD_JPY" in message
        assert "1000" in message
        assert "order_123" in message

    @patch("src.notification.requests.post")
    def test_send_trade_log_with_additional_fields(self, mock_post):
        """テスト: 追加フィールド付きのトレードログ"""
        mock_response = MagicMock()
        mock_post.return_value = mock_response

        notifier = Notifier(webhook_url="https://discord.webhook")
        trade_details = {
            "instrument": "EUR_USD",
            "units": -500,
            "id": "order_456",
            "entry_price": 1.0850,
            "stop_loss": 1.0800,
            "take_profit": 1.0950
        }
        notifier.send_trade_log(trade_details)

        args, kwargs = mock_post.call_args
        message = kwargs["json"]["content"]
        assert "EUR_USD" in message
        assert "-500" in message
        assert "order_456" in message

    @patch("src.notification.requests.post")
    def test_send_trade_log_missing_fields(self, mock_post):
        """テスト: 必須フィールドが不足している場合"""
        mock_response = MagicMock()
        mock_post.return_value = mock_response

        notifier = Notifier(webhook_url="https://discord.webhook")
        trade_details = {
            "instrument": "GBP_USD"
            # 'units' と 'id' が不足
        }
        notifier.send_trade_log(trade_details)

        # Should still work with None for missing keys
        args, kwargs = mock_post.call_args
        message = kwargs["json"]["content"]
        assert "GBP_USD" in message
        assert "None" in message

    @patch("src.notification.requests.post")
    def test_send_trade_log_empty_dict(self, mock_post):
        """テスト: 空の辞書でのトレードログ"""
        mock_response = MagicMock()
        mock_post.return_value = mock_response

        notifier = Notifier(webhook_url="https://discord.webhook")
        notifier.send_trade_log({})

        args, kwargs = mock_post.call_args
        message = kwargs["json"]["content"]
        assert "Trade Executed" in message
        assert "None" in message

    def test_send_trade_log_to_stdout(self, capsys):
        """テスト: トレードログを stdout に出力"""
        notifier = Notifier(webhook_url=None)
        trade_details = {
            "instrument": "AUD_USD",
            "units": 2000,
            "id": "order_789"
        }
        notifier.send_trade_log(trade_details)

        captured = capsys.readouterr()
        assert "Trade Executed" in captured.out
        assert "AUD_USD" in captured.out
        assert "2000" in captured.out

    @patch("src.notification.requests.post")
    def test_send_trade_log_with_error_fallback(self, mock_post, capsys):
        """テスト: トレードログ送信エラーと fallback"""
        mock_post.side_effect = requests.exceptions.ConnectionError("Network error")

        notifier = Notifier(webhook_url="https://discord.webhook")
        trade_details = {
            "instrument": "USD_CAD",
            "units": 1500,
            "id": "order_999"
        }
        notifier.send_trade_log(trade_details)

        captured = capsys.readouterr()
        assert "NOTIFICATION ERROR" in captured.out
        assert "NOTIFICATION FALLBACK" in captured.out


class TestNotifierEdgeCases:
    """Test edge cases and unusual scenarios."""

    def test_notifier_empty_string_webhook_url(self):
        """テスト: 空文字列の Webhook URL"""
        notifier = Notifier(webhook_url="")
        # Empty string is falsy, so should use stdout
        assert not notifier.webhook_url

    @patch("src.notification.requests.post")
    def test_send_message_empty_string(self, mock_post):
        """テスト: 空文字列メッセージの送信"""
        mock_response = MagicMock()
        mock_post.return_value = mock_response

        notifier = Notifier(webhook_url="https://discord.webhook")
        notifier.send_message("")

        args, kwargs = mock_post.call_args
        assert kwargs["json"]["content"] == ""

    @patch("src.notification.requests.post")
    def test_send_message_only_whitespace(self, mock_post):
        """テスト: 空白のみのメッセージ"""
        mock_response = MagicMock()
        mock_post.return_value = mock_response

        notifier = Notifier(webhook_url="https://discord.webhook")
        notifier.send_message("   \n\t  ")

        args, kwargs = mock_post.call_args
        assert kwargs["json"]["content"] == "   \n\t  "

    @patch("src.notification.requests.post")
    def test_send_message_unicode_emoji(self, mock_post):
        """テスト: Unicode絵文字の送信"""
        mock_response = MagicMock()
        mock_post.return_value = mock_response

        notifier = Notifier(webhook_url="https://discord.webhook")
        message = "📈 📉 💰 🔥 💎"
        notifier.send_message(message)

        args, kwargs = mock_post.call_args
        assert kwargs["json"]["content"] == message

    @patch("src.notification.requests.post")
    def test_send_message_json_special_chars(self, mock_post):
        """テスト: JSON特殊文字を含むメッセージ"""
        mock_response = MagicMock()
        mock_post.return_value = mock_response

        notifier = Notifier(webhook_url="https://discord.webhook")
        message = 'Test with "quotes" and \\backslash\\'
        notifier.send_message(message)

        args, kwargs = mock_post.call_args
        assert kwargs["json"]["content"] == message


class TestNotifierMultipleCalls:
    """Test multiple consecutive notifications."""

    @patch("src.notification.requests.post")
    def test_multiple_messages_sequential(self, mock_post):
        """テスト: 複数メッセージの順次送信"""
        mock_response = MagicMock()
        mock_post.return_value = mock_response

        notifier = Notifier(webhook_url="https://discord.webhook")
        messages = ["Message 1", "Message 2", "Message 3"]

        for msg in messages:
            notifier.send_message(msg)

        assert mock_post.call_count == 3

    @patch("src.notification.requests.post")
    def test_multiple_trade_logs(self, mock_post):
        """テスト: 複数トレードログの送信"""
        mock_response = MagicMock()
        mock_post.return_value = mock_response

        notifier = Notifier(webhook_url="https://discord.webhook")
        trades = [
            {"instrument": "USD_JPY", "units": 1000, "id": "order_1"},
            {"instrument": "EUR_USD", "units": 500, "id": "order_2"},
            {"instrument": "GBP_USD", "units": -1000, "id": "order_3"}
        ]

        for trade in trades:
            notifier.send_trade_log(trade)

        assert mock_post.call_count == 3

    def test_mixed_messages_and_trade_logs_stdout(self, capsys):
        """テスト: メッセージとトレードログの混合出力"""
        notifier = Notifier(webhook_url=None)

        notifier.send_message("Trade started")
        notifier.send_trade_log({
            "instrument": "USD_JPY",
            "units": 1000,
            "id": "order_1"
        })
        notifier.send_message("Trade completed")

        captured = capsys.readouterr()
        assert "Trade started" in captured.out
        assert "Trade Executed" in captured.out
        assert "Trade completed" in captured.out
