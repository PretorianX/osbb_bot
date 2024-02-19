import copy

from celery_app import app
from modules.scrappers import ChernivtsiOblEnergo
from modules.serializers import html_table_to_dict, TelegramChernivtsiOblEnergo
from modules.notifications import TelegramNotificationChannel
from datetime import datetime
import json
import configparser
from pathlib import Path

last_results = None

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


@app.task
def run_check_coe():
    global last_results
    config = configparser.ConfigParser()
    config.read('config.cfg')
    telegram_api_key = config['telegram']['api_key']
    telegram_chat_ids_raw = config['telegram']['chat_ids'].split(',')
    uniq_telegram_chat_ids = [[x for i, x in enumerate(telegram_chat_ids_raw) if x not in telegram_chat_ids_raw[:i]]]
    date = datetime.now().strftime("%d.%m.%Y")
    city = config['tasks']['city']
    street = config['tasks']['street']
    if config['tasks']['date']:
        date = config['tasks']['date']
    coe = check_coe(street=street, city=city, date=date)
    # Path to the file where the last check results are stored

    print(f"{date} {city} {street} COMPARE: coe {coe} \n\n last_results {last_results}")
    # Compare current results with last results
    if coe != last_results:
        last_results = copy.deepcopy(coe)

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
            print(f"{date}: {city} {street} Number of emergency shutdowns: {len(coe['emergency'])}, "
                  f"number of planned shutdowns: {len(coe['planned'])}")

