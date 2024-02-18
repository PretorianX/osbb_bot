from modules.scrappers import ChernivtsiOblEnergo
from modules.serializers import html_table_to_dict, TelegramChernivtsiOblEnergo
from modules.notifications import TelegramNotificationChannel
from datetime import datetime
import json


def check_coe(street, city, date, *args, **kwargs):
    street = street
    city = city
    coe_types = [0, 1]  # 1 - planned, 0 - emergency
    coe_shutdowns = {"emergency": [], "planned": []}

    for coe_type in coe_types:
        coe = ChernivtsiOblEnergo()
        coe_result = coe.fetch(data={
            "v_date": date,
            "v_type": coe_type,
            "v_diln": 12,
            "v_city": city,
            "v_street": street,
            "v_house": None,
            "v_sort_field": 4,
            "v_sort_type": 0,
            "v_page": 1,
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            },
        )

        html_table = json.loads(coe_result['message'])
        if coe_type:
            coe_shutdowns['planned'] += html_table_to_dict(html_table['data'])
        else:
            coe_shutdowns['emergency'] += html_table_to_dict(html_table['data'])
    return coe_shutdowns


if __name__ == "__main__":
    import configparser
    config = configparser.ConfigParser()
    config.read('config.cfg')
    telegram_api_key = config['telegram']['api_key']
    telegram_chat_ids_raw = config['telegram']['chat_ids'].split(',')
    uniq_telegram_chat_ids = [[x for i, x in enumerate(telegram_chat_ids_raw) if x not in telegram_chat_ids_raw[:i]]]
    date = datetime.now().strftime("%d.%m.%Y")
    date = '20.02.2024'     # debug mode
    coe = check_coe(street="", city="Чернівці", date=date)
    if config['telegram']['enabled']:
        serialized_notification_obj = TelegramChernivtsiOblEnergo()
        for chat_id in uniq_telegram_chat_ids[0]:
            telegram = TelegramNotificationChannel(telegram_api_key, chat_id)
            if coe['emergency']:
                for shutdown in coe['emergency']:
                    shutdown.append("emergency")
                    telegram.send_notification(serialized_notification_obj.serialize(shutdown))
            if coe['planned']:
                for shutdown in coe['planned']:
                    shutdown.append("planned")
                    telegram.send_notification(serialized_notification_obj.serialize(shutdown))
                    break
        print(f"{date}: Number of emergency shutdowns: {len(coe['emergency'])}, "
              f"number of planned shutdowns: {len(coe['planned'])}")