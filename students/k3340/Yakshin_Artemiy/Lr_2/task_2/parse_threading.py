"""Параллельный парсинг с помощью threading.

I/O-bound задача (сетевой запрос ждёт ответа сервера), поэтому GIL
отпускается на время системных вызовов — threading реально помогает.
"""
from __future__ import annotations

import threading
import time

import requests
from bs4 import BeautifulSoup

from task_2.db import HEADERS, URLS, init_db, save_title


def parse_and_save(url: str) -> None:
    try:
        resp = requests.get(url, timeout=10, headers=HEADERS)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        title = (soup.title.string or "").strip() if soup.title else "<no-title>"
    except Exception as e:
        title = f"<error: {e.__class__.__name__}>"
    save_title(url, title)
    print(f"[threading] {url} -> {title!r}")


def main() -> None:
    init_db()
    threads = [threading.Thread(target=parse_and_save, args=(u,)) for u in URLS]
    t0 = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    elapsed = time.perf_counter() - t0
    print(f"[threading] total: {len(URLS)} urls in {elapsed:.3f}s")


if __name__ == "__main__":
    main()
