import requests
from abc import ABC, abstractmethod


class Scrapper(ABC):
    response = {
        "status": None,
        "message": None
    }

    @abstractmethod
    def fetch(self, method, url, headers, data) -> dict:
        pass


class NotificationChannel(ABC):
    result = {}

    @abstractmethod
    def send_notification(self, message) -> dict:
        return self.result


class ChernivtsiOblEnergo(Scrapper):
    """
    Check for shutdowns in Chernivtsi OblEnergo
    https://oblenergo.cv.ua/shutdowns/
    """
    response = {}

    def fetch(self, method='POST', url='https://oblenergo.cv.ua/shutdowns/planovi_avarijni_result.php', headers=None, data=None) -> dict:
        try:
            response = requests.request(method=method,
                                        url=url,
                                        headers=headers, data=data)
            if not 'Content-Type' in headers:
                headers['Content-Type'] = 'application/x-www-form-urlencoded'
            self.response["status"] = response.status_code
            self.response["message"] = response.text
        except requests.exceptions.RequestException as e:
            self.response["status"] = 500
            self.response["message"] = f"Error fetching data: {e}"
        return self.response
