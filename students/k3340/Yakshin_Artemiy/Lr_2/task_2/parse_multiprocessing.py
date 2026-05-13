"""Параллельный парсинг с помощью multiprocessing.

Под I/O-bound задачи процессы — не лучший выбор: запускать
отдельный интерпретатор ради `requests.get()` дорого. Но согласно
заданию вариант должен быть, и сравнение наглядное.
"""
from __future__ import annotations

import time
from multiprocessing import Pool

import requests
from bs4 import BeautifulSoup

from task_2.db import HEADERS, URLS, init_db, save_title


def parse_and_save(url: str) -> str:
    try:
        resp = requests.get(url, timeout=10, headers=HEADERS)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        title = (soup.title.string or "").strip() if soup.title else "<no-title>"
    except Exception as e:
        title = f"<error: {e.__class__.__name__}>"
    save_title(url, title)
    print(f"[multiprocessing] {url} -> {title!r}")
    return title


def main() -> None:
    init_db()
    t0 = time.perf_counter()
    with Pool(processes=min(8, len(URLS))) as pool:
        pool.map(parse_and_save, URLS)
    elapsed = time.perf_counter() - t0
    print(f"[multiprocessing] total: {len(URLS)} urls in {elapsed:.3f}s")


if __name__ == "__main__":
    main()
