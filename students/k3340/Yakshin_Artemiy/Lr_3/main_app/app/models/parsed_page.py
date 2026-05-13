"""Сущность для хранения результатов парсинга."""
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class ParsedPageDefault(SQLModel):
    url: str
    title: str


class ParsedPage(ParsedPageDefault, table=True):
    __tablename__ = "parsed_page"

    id: Optional[int] = Field(default=None, primary_key=True)
    url: str = Field(index=True)
    parsed_at: datetime = Field(default_factory=datetime.utcnow)


class ParsedPageRead(ParsedPageDefault):
    id: int
    parsed_at: datetime
