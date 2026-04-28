from celery import Celery
from core.config import settings

broker = f"{settings.REDIS_URL}/0"
backend = f"{settings.REDIS_URL}/1"

celery = Celery(
    "billing_workers",
    broker=broker,
    backend=backend,
)

celery.conf.task_routes = {
    "tasks.webhook_tasks.*": {"queue": "webhooks"},
    "tasks.billing_tasks.*": {"queue": "billing"},
}
celery.conf.task_acks_late = True
celery.conf.worker_prefetch_multiplier = 1
celery.conf.task_soft_time_limit = 300