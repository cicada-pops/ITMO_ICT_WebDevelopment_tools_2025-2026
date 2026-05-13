"""Подсчёт суммы 1..N с помощью threading.

CPU-bound задача, поэтому из-за GIL реального ускорения почти нет —
запускается ради сравнения с multiprocessing и asyncio.
"""
from __future__ import annotations

import os
import threading
import time

N = int(os.getenv("N", "100_000_000"))
WORKERS = int(os.getenv("WORKERS", "4"))


def calculate_sum(start: int, end: int, results: list[int], idx: int) -> None:
    """Считает сумму чисел [start, end] и кладёт её в results[idx]."""
    total = 0
    for i in range(start, end + 1):
        total += i
    results[idx] = total


def main() -> None:
    chunk = N // WORKERS
    threads: list[threading.Thread] = []
    results: list[int] = [0] * WORKERS

    t0 = time.perf_counter()
    for i in range(WORKERS):
        start = i * chunk + 1
        end = N if i == WORKERS - 1 else (i + 1) * chunk
        t = threading.Thread(target=calculate_sum, args=(start, end, results, i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    elapsed = time.perf_counter() - t0

    total = sum(results)
    expected = N * (N + 1) // 2
    assert total == expected, f"{total} != {expected}"
    print(f"[threading]      N={N}, workers={WORKERS}, sum={total}, time={elapsed:.3f}s")


if __name__ == "__main__":
    main()
