from celery import Celery
import os

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
app = Celery("tasks", broker=CELERY_BROKER_URL)

app.conf.task_routes = {
    "app.services.job_queue.process_svg_job": {"queue": "svg"},
}

# ✅ ADD THIS LINE to register the task with Celery
from app.services import job_queue
