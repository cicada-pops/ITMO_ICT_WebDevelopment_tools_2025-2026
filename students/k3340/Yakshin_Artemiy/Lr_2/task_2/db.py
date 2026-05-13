"""Общий слой БД для всех трёх программ Task 2.

Используется та же база `hackathons_db` из ЛР1; здесь создаётся
дополнительная таблица `parsed_page` для результатов парсинга.
"""
from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from sqlmodel import Field, Session, SQLModel, create_engine

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

DB_URL = os.getenv("DB_ADMIN", "postgresql://postgres:postgres@localhost/hackathons_db")
engine = create_engine(DB_URL, echo=False)


class ParsedPage(SQLModel, table=True):
    """Заголовок страницы, полученный парсингом."""
    __tablename__ = "parsed_page"

    id: Optional[int] = Field(default=None, primary_key=True)
    url: str = Field(index=True)
    title: str
    parsed_at: datetime = Field(default_factory=datetime.utcnow)


def init_db() -> None:
    SQLModel.metadata.create_all(engine, tables=[ParsedPage.__table__])


def save_title(url: str, title: str) -> None:
    """Атомарно сохраняет одну запись. Используется в синхронных вариантах."""
    with Session(engine) as session:
        session.add(ParsedPage(url=url, title=title))
        session.commit()


def save_titles_bulk(rows: list[tuple[str, str]]) -> None:
    """Сохраняет пачку записей одной транзакцией (для async-варианта)."""
    with Session(engine) as session:
        for url, title in rows:
            session.add(ParsedPage(url=url, title=title))
        session.commit()


HEADERS: dict[str, str] = {
    "User-Agent": "Mozilla/5.0 (Lr_2 parser; educational use)"
}

URLS: list[str] = [
    "https://example.com/",
    "https://www.python.org/",
    "https://docs.python.org/3/library/asyncio.html",
    "https://docs.python.org/3/library/threading.html",
    "https://docs.python.org/3/library/multiprocessing.html",
    "https://fastapi.tiangolo.com/",
    "https://sqlmodel.tiangolo.com/",
    "https://www.postgresql.org/",
    "https://en.wikipedia.org/wiki/Hackathon",
    "https://en.wikipedia.org/wiki/Concurrency_(computer_science)",
    "https://en.wikipedia.org/wiki/Thread_(computing)",
    "https://en.wikipedia.org/wiki/Process_(computing)",
]
