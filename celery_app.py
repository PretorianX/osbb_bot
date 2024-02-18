from celery import Celery
import configparser
from datetime import timedelta

config = configparser.ConfigParser()
config.read('config.cfg')
scan_interval = config['celery']['scan_interval']

# Initialize your Celery app
# The name 'osbb_bot' here is arbitrary and does not need to match your directory name
app = Celery('osbb_bot', broker='redis://redis:6379/0')

# Since 'celery_app.py' and 'bot.py' are in the same directory,
# and assuming you're running the Celery worker from this directory,
# you can just use 'bot' as the module name for autodiscovery
app.autodiscover_tasks(['bot'], force=True)


app.conf.beat_schedule = {
    'run-check-coe-every-n-minutes': {
        'task': 'bot.run_check_coe',
        'schedule': timedelta(minutes=int(scan_interval)),
    },
}