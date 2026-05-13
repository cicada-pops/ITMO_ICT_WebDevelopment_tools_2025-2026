"""Параллельный парсинг с помощью asyncio + aiohttp.

Для I/O-bound нагрузки это самый дешёвый из трёх подходов: одна нить,
один процесс, переключение задач происходит ровно тогда, когда воркер
ждёт сетевой ответ.
"""
from __future__ import annotations

import asyncio
import time

import aiohttp
from bs4 import BeautifulSoup

from task_2.db import HEADERS, URLS, init_db, save_titles_bulk


async def parse_and_save(session: aiohttp.ClientSession, url: str) -> tuple[str, str]:
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            resp.raise_for_status()
            html = await resp.text()
        soup = BeautifulSoup(html, "html.parser")
        title = (soup.title.string or "").strip() if soup.title else "<no-title>"
    except Exception as e:
        title = f"<error: {e.__class__.__name__}>"
    print(f"[asyncio] {url} -> {title!r}")
    return url, title


async def main() -> None:
    init_db()
    t0 = time.perf_counter()
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        rows = await asyncio.gather(*(parse_and_save(session, u) for u in URLS))
    # запись в БД одной транзакцией — psycopg2 не умеет асинхронно,
    # а гонять отдельную сессию на каждый url дороже, чем сам пакетный
    # инсерт после сбора всех заголовков.
    save_titles_bulk(list(rows))
    elapsed = time.perf_counter() - t0
    print(f"[asyncio] total: {len(URLS)} urls in {elapsed:.3f}s")


if __name__ == "__main__":
    asyncio.run(main())
