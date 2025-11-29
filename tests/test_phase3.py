import pytest
from unittest.mock import patch, MagicMock
from src.execution import OrderExecutor
from src.notification import Notifier

def test_execution_mock():
    # Test Mock Mode
    with patch("src.config.Config.ENV", "mock"):
        executor = OrderExecutor()
        result = executor.execute_order("USD_JPY", 1000)
        assert result["id"] == "mock_order_id"
        assert result["units"] == 1000

def test_notification_mock(capsys):
    # Test Mock Notification (stdout)
    notifier = Notifier(webhook_url=None)
    notifier.send_message("Test Message")
    
    captured = capsys.readouterr()
    assert "[NOTIFICATION (STDOUT)] Test Message" in captured.out

def test_notification_discord():
    # Test Discord Webhook call
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        notifier = Notifier(webhook_url="http://fake.url")
        notifier.send_message("Test Discord")
        
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs['json']['content'] == "Test Discord"
