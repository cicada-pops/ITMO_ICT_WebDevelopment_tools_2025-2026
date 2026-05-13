"""Подсчёт суммы 1..N с помощью multiprocessing.

Каждый воркер — отдельный процесс с собственным интерпретатором,
поэтому GIL не мешает и для CPU-bound задачи виден настоящий
параллелизм.
"""
from __future__ import annotations

import os
import time
from multiprocessing import Pool

N = int(os.getenv("N", "100_000_000"))
WORKERS = int(os.getenv("WORKERS", "4"))


def calculate_sum(bounds: tuple[int, int]) -> int:
    start, end = bounds
    total = 0
    for i in range(start, end + 1):
        total += i
    return total


def main() -> None:
    chunk = N // WORKERS
    ranges: list[tuple[int, int]] = []
    for i in range(WORKERS):
        start = i * chunk + 1
        end = N if i == WORKERS - 1 else (i + 1) * chunk
        ranges.append((start, end))

    t0 = time.perf_counter()
    with Pool(processes=WORKERS) as pool:
        partials = pool.map(calculate_sum, ranges)
    elapsed = time.perf_counter() - t0

    total = sum(partials)
    expected = N * (N + 1) // 2
    assert total == expected, f"{total} != {expected}"
    print(f"[multiprocessing] N={N}, workers={WORKERS}, sum={total}, time={elapsed:.3f}s")


if __name__ == "__main__":
    main()
