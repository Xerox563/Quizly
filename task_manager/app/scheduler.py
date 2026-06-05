from apscheduler.schedulers.background import BackgroundScheduler
from app.celery_app import send_reminder
import logging

scheduler = BackgroundScheduler()

# Schedule job
@scheduler.scheduled_job(
    "interval",
    seconds=30,
    id="reminder_job"
)

def reminder_job():
    print("Running Scheduler")
    for task_id in [1,2,3]:
        send_reminder.delay(task_id)

def start_scheduler():
    if not scheduler.running:
        scheduler.start()        

def stop_scheduler():
    if scheduler.running:
        scheduler.start()   