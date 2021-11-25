"""
Расписание тасков Celery
"""
from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cfg.settings')
app = Celery('backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'process-crm-requests': {
        'task': 'amocrm.tasks.job_process_requests',
        'schedule': crontab(minute='0-59')
    },
    'calculate-partners-fee': {
        'task': 'appuser.tasks.job_change_user_target',
        'schedule': crontab(day_of_month='1', hour='0')
    },
    'refresh-cdek-cities-list': {
        'task': 'shop.tasks.get_cdek_cities_list',
        'schedule': crontab(minute='0', hour='20')
    }
}
