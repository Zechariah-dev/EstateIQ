import os

from celery import Celery
from celery.schedules import crontab
from decouple import config

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EstateIQAPI.settings')

# used redis for saving task and running task
app = Celery('EstateIQAPI', broker=config("CELERY_BROKER_URL"), backend=config("CELERY_BROKER_URL"))
app.config_from_object('django.conf:settings')

# Load task modules from all registered Django app configs.
app.conf.broker_url = config("CELERY_BROKER_URL")

#  this is used to make an automation either send mail during a specific time
#  or delete some stuff or more
app.conf.beat_schedule = {
    #  This is used to penalise users who haven't paid their utilities
    "penalise_users_on_estate_utilities": {
        "task": 'estate_utilities.tasks.penalise_users_on_estate_utilities',
        "schedule": crontab(hour=23),
    },
    #  This is used to remove the penalty on the existing user if the penalty was deleted
    "remove_penalty_not_existing_on_utility_penalty": {
        "task": 'estate_utilities.tasks.remove_penalty_not_existing_on_utility_penalty',
        "schedule": crontab(hour=23),
    },

}


@app.task
def debug_task():
    print(f'Request: ')
