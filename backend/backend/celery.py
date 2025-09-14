import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
app = Celery("backend")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")


app.conf.beat_schedule = {
    "fetch-daily-health-tips": {
        "task": "api.tasks.fetch_daily_health_tip",
        "schedule": crontab(hour=8, minute=0),  
    },
    "export-unanswered-cleanup": {
        "task": "api.tasks.export_unanswered",
        "schedule": crontab(hour=0, minute=0),
    },
}
