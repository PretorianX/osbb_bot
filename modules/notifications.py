import time
import requests
from abc import ABC, abstractmethod


class NotificationChannel(ABC):
    @abstractmethod
    def send_notification(self, message):
        pass


class TelegramNotificationChannel(NotificationChannel):
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id

    def send_notification(self, message):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        data = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "MarkdownV2"
        }
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            print("Notification sent successfully")
        except requests.exceptions.RequestException as e:
            print(f"Error sending notification: {e}")
