"""Celery-клиент. Используется в FastAPI только для отправки задач
в очередь и опроса статуса — сами задачи определены в пакете worker.
"""
from celery import Celery

from app.config import settings

celery_app = Celery(
    "lr3",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)
celery_app.conf.task_default_queue = "parse"

# Имя задачи синхронизировано с воркером (worker.tasks.parse_url).
PARSE_TASK_NAME = "worker.tasks.parse_url"
