"""
Celery application configuration for async task processing.
"""
from celery import Celery
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "santa_tasks",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks"]
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task execution settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Beat schedule for periodic tasks
    beat_schedule={
        "fetch-emails-every-minute": {
            "task": "app.tasks.fetch_emails_task",
            "schedule": settings.email_fetch_interval,  # seconds
        },
    },
    
    # Result backend settings
    result_expires=3600,  # 1 hour
)
