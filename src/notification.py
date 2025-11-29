import requests
import os

class Notifier:
    def __init__(self, webhook_url=None):
        self.webhook_url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL")

    def send_message(self, message):
        """
        Send a message to Discord or print to stdout.
        """
        if self.webhook_url:
            try:
                data = {"content": message}
                response = requests.post(self.webhook_url, json=data)
                response.raise_for_status()
            except Exception as e:
                print(f"[NOTIFICATION ERROR] Failed to send to Discord: {e}")
                print(f"[NOTIFICATION FALLBACK] {message}")
        else:
            print(f"[NOTIFICATION (STDOUT)] {message}")

    def send_trade_log(self, trade_details):
        msg = (
            f"**Trade Executed**\n"
            f"Instrument: {trade_details.get('instrument')}\n"
            f"Units: {trade_details.get('units')}\n"
            f"ID: {trade_details.get('id')}"
        )
        self.send_message(msg)
