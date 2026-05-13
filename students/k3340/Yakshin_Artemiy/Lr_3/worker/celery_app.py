"""Celery-приложение воркера. Регистрирует задачи из worker.tasks."""
import os

from celery import Celery

BROKER = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")

celery_app = Celery(
    "lr3",
    broker=BROKER,
    backend=BACKEND,
    include=["worker.tasks"],
)

celery_app.conf.task_default_queue = "parse"
celery_app.conf.result_expires = 3600
