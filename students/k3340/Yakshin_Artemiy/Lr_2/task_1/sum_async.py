"""Подсчёт суммы 1..N с помощью asyncio.

CPU-bound задача и одна нить событийного цикла — корутины выполняются
последовательно. Asyncio здесь нужен скорее как точка отсчёта: он не
ускоряет арифметику, в отличие от multiprocessing.
"""
from __future__ import annotations

import asyncio
import os
import time

N = int(os.getenv("N", "100_000_000"))
WORKERS = int(os.getenv("WORKERS", "4"))


async def calculate_sum(start: int, end: int) -> int:
    total = 0
    for i in range(start, end + 1):
        total += i
    return total


async def main() -> None:
    chunk = N // WORKERS
    coros = []
    for i in range(WORKERS):
        start = i * chunk + 1
        end = N if i == WORKERS - 1 else (i + 1) * chunk
        coros.append(calculate_sum(start, end))

    t0 = time.perf_counter()
    partials = await asyncio.gather(*coros)
    elapsed = time.perf_counter() - t0

    total = sum(partials)
    expected = N * (N + 1) // 2
    assert total == expected, f"{total} != {expected}"
    print(f"[asyncio]         N={N}, workers={WORKERS}, sum={total}, time={elapsed:.3f}s")


if __name__ == "__main__":
    asyncio.run(main())
