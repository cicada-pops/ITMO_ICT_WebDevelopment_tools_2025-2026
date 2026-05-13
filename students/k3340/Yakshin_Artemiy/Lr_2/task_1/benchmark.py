"""Запуск всех трёх вариантов подряд с одной и той же N и выводом таблицы."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
PY = sys.executable

SCRIPTS = ["sum_threading.py", "sum_multiprocessing.py", "sum_async.py"]


def main() -> None:
    for name in SCRIPTS:
        subprocess.run([PY, str(HERE / name)], check=True)


if __name__ == "__main__":
    main()
