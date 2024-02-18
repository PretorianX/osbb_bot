import datetime

from bs4 import BeautifulSoup
from abc import ABC, abstractmethod


def html_table_to_dict(html_content):
    # Parse the HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the table
    table = soup.find('tbody')

    # Prepare the dictionary
    table_data = []

    # Iterate over rows
    for row in table.find_all('tr')[1:]:  # Skipping the header row
        cells = row.find_all('td')
        if len(cells):  # Cell length should match header length
            row_data = [cell.text for cell in cells]
            table_data.append(row_data)

    return table_data


class MaintenanceReport(ABC):
    """
    Converts reports from different sources to a common format
    """
    planned = False
    service = None
    region = None
    city = None
    street = None
    tst_start = None
    tst_end = None
    header = None

    @abstractmethod
    def serialize(self, data) -> str:
        return f"Сервіс: {self.service}\n" \
               f"Регіон: {self.region}\n" \
               f"Місто: {self.city}\n" \
               f"Вулиця: {self.street}\n" \
               f"Початок події: {self.tst_start}\n" \
               f"Завершення події: {self.tst_end}\n"


class TelegramChernivtsiOblEnergo(MaintenanceReport):

    @staticmethod
    def escape_markdown_v2(text):
        """
        Escapes characters for MarkdownV2 formatting in Telegram.
        """
        escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        # Escape each character with a backslash
        for char in escape_chars:
            text = text.replace(char, '\\' + char)
        return text

    def serialize(self, data: list) -> str:
        self.planned = "Планове" if data[5] == "planned" else "Аварійне"
        self.service = "ЧернівціОблЕнерго"
        self.region = self.escape_markdown_v2(data[0])
        self.city = self.escape_markdown_v2(data[1])
        self.street = self.escape_markdown_v2(data[2])
        self.tst_start = self.escape_markdown_v2(data[3])
        self.tst_end = self.escape_markdown_v2(data[4])
        self.header = f"УВАГА! {self.planned} відключення світла"
        self.header = self.escape_markdown_v2(self.header)
        return f"💡 *{self.header}*\n\n" \
               f"Сервіс: *{self.service}*\n" \
               f"Регіон: {self.region}\n" \
               f"Місто: {self.city}\n" \
               f"Вулиця: {self.street}\n" \
               f"Початок: *{self.tst_start}*\n" \
               f"Завершення: *{self.tst_end}*\n"
