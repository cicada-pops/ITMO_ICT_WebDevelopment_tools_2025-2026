"""Celery-задачи воркера."""
from __future__ import annotations

import os

import requests

from worker.celery_app import celery_app

PARSER_URL = os.getenv("PARSER_URL", "http://parser:8001")


@celery_app.task(name="worker.tasks.parse_url", bind=True, max_retries=2)
def parse_url(self, url: str) -> dict:
    """Делегирует парсинг в сервис parser.

    Воркер не парсит сам, а вызывает HTTP-сервис parser — благодаря
    этому логика парсинга существует ровно в одном месте, а worker
    отвечает только за асинхронность и ретраи.
    """
    try:
        resp = requests.post(
            f"{PARSER_URL}/parse",
            json={"url": url},
            timeout=20,
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise self.retry(exc=exc, countdown=5)
    return resp.json()
