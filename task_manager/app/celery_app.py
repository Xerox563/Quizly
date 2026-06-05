from celery import Celery
from app.services.email_service import send_email_service
from app.services.report_service import generate_report_service

celery_app = Celery("Tasks") # Creates Celery application.

celery_app.conf.update(
    task_always_eager = True,
    task_eager_propagate = True
)

@celery_app.task  # Marks function as: Background Job
def send_email(email,subject):
    send_email_service(email, subject)

@celery_app.task
def generate_report(task_id):
    generate_report_service(task_id)

@celery_app.task
def send_reminder(task_id):
    print(f"Reminder sent for task {task_id}")