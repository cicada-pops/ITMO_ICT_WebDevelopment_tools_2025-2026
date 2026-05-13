"""Прогон всех трёх вариантов парсинга подряд."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable

MODULES = [
    "task_2.parse_threading",
    "task_2.parse_multiprocessing",
    "task_2.parse_async",
]


def main() -> None:
    for mod in MODULES:
        subprocess.run([PY, "-m", mod], check=True, cwd=ROOT)


if __name__ == "__main__":
    main()
