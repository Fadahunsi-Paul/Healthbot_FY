from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import csv
import os
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from .model.unanswered import Unanswered
from .utils.utils import fetch_daily_health_tip


def send_health_tips():
    fetch_daily_health_tip(force_refresh=True)
    return "✅ Daily health tips sent"


def export_unanswered():
    today_str = timezone.now().strftime("%Y-%m-%d")
    export_filename = f"unanswered_export_{today_str}.csv"
    export_path = os.path.join(settings.BASE_DIR, "exports", export_filename)

    os.makedirs(os.path.dirname(export_path), exist_ok=True)

    with open(export_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Question", "Answer"])  
        for item in Unanswered.objects.filter(is_answered=True):
            writer.writerow([item.question, item.answer])

    cutoff = timezone.now() - timedelta(days=7)
    deleted, _ = Unanswered.objects.filter(created_at__lt=cutoff).delete()

    return f"✅ Export complete → {export_path}, deleted {deleted} old records"

scheduler = BackgroundScheduler()

scheduler.add_job(send_health_tips, CronTrigger(hour=8, minute=0), id="send_health_tips")
scheduler.add_job(export_unanswered, CronTrigger(day_of_week="sun", hour=0, minute=0), id="export_unanswered")
scheduler.start()
