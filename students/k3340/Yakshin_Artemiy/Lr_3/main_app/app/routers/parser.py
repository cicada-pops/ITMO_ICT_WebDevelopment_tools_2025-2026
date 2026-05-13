"""Эндпоинты для работы с парсером.

- POST /parse        — синхронный вызов сервиса parser по HTTP.
- POST /parse-async  — постановка задачи в Celery, возврат task_id.
- GET  /parse/status/{task_id} — статус задачи Celery.
- GET  /parse       — список последних результатов из БД.
"""
from typing import List, Optional

import requests
from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl
from sqlmodel import Session, desc, select

from app.celery_app import PARSE_TASK_NAME, celery_app
from app.config import settings
from app.connection import get_session
from app.models.parsed_page import ParsedPage, ParsedPageRead

router = APIRouter(prefix="/parse", tags=["parser"])


class ParseRequest(BaseModel):
    url: HttpUrl


class ParseSyncResponse(BaseModel):
    url: str
    title: str
    id: int


class ParseAsyncResponse(BaseModel):
    task_id: str
    status: str = "queued"


class ParseStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[dict] = None


@router.post("", response_model=ParseSyncResponse)
def parse_sync(req: ParseRequest) -> ParseSyncResponse:
    """Синхронно проксирует запрос в сервис parser и возвращает результат."""
    try:
        resp = requests.post(
            f"{settings.PARSER_URL}/parse",
            json={"url": str(req.url)},
            timeout=15,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"parser unavailable: {e}")
    return ParseSyncResponse(**resp.json())


@router.post("/async", response_model=ParseAsyncResponse)
def parse_async(req: ParseRequest) -> ParseAsyncResponse:
    """Ставит задачу в очередь Celery, мгновенно возвращает task_id."""
    task = celery_app.send_task(PARSE_TASK_NAME, args=[str(req.url)])
    return ParseAsyncResponse(task_id=task.id)


@router.get("/status/{task_id}", response_model=ParseStatusResponse)
def parse_status(task_id: str) -> ParseStatusResponse:
    res = AsyncResult(task_id, app=celery_app)
    payload: Optional[dict] = None
    if res.successful():
        payload = res.result if isinstance(res.result, dict) else {"value": res.result}
    elif res.failed():
        payload = {"error": str(res.result)}
    return ParseStatusResponse(task_id=task_id, status=res.status, result=payload)


@router.get("", response_model=List[ParsedPageRead])
def list_parsed(
    limit: int = 20,
    session: Session = Depends(get_session),
) -> List[ParsedPage]:
    stmt = select(ParsedPage).order_by(desc(ParsedPage.parsed_at)).limit(limit)
    return session.exec(stmt).all()
