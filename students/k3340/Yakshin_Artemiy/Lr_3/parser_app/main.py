"""Самостоятельный сервис-парсер.

Принимает POST /parse {url}, забирает страницу через requests,
извлекает <title> через BeautifulSoup и сохраняет результат в ту же
БД, что и основное приложение (таблица parsed_page).
"""
from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from sqlmodel import Field, Session, SQLModel, create_engine

DB_URL = os.getenv(
    "DB_ADMIN", "postgresql://postgres:postgres@db:5432/hackathons_db"
)
HEADERS = {"User-Agent": "Mozilla/5.0 (Lr_3 parser; educational use)"}

engine = create_engine(DB_URL, echo=False)


class ParsedPage(SQLModel, table=True):
    __tablename__ = "parsed_page"

    id: Optional[int] = Field(default=None, primary_key=True)
    url: str = Field(index=True)
    title: str
    parsed_at: datetime = Field(default_factory=datetime.utcnow)


def init_db() -> None:
    SQLModel.metadata.create_all(engine, tables=[ParsedPage.__table__])


app = FastAPI(
    title="Parser Service",
    description="Самостоятельный сервис-парсер для Lr_3.",
    version="1.0.0",
)


class ParseRequest(BaseModel):
    url: HttpUrl


class ParseResponse(BaseModel):
    id: int
    url: str
    title: str


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/parse", response_model=ParseResponse)
def parse(req: ParseRequest) -> ParseResponse:
    url = str(req.url)
    try:
        resp = requests.get(url, timeout=10, headers=HEADERS)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"fetch failed: {e}")

    soup = BeautifulSoup(resp.text, "html.parser")
    title = (soup.title.string or "").strip() if soup.title else "<no-title>"

    with Session(engine) as session:
        row = ParsedPage(url=url, title=title)
        session.add(row)
        session.commit()
        session.refresh(row)

    return ParseResponse(id=row.id, url=row.url, title=row.title)
