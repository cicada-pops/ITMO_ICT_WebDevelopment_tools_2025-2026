# Задача 1. Сумма чисел тремя подходами

## Постановка

Посчитать сумму всех чисел от 1 до `N`, разбив диапазон на несколько
подзадач и запустив их параллельно тремя способами: `threading`,
`multiprocessing`, `asyncio`. Замерить и сравнить время.

### Замечание про `N`

В исходном задании `N = 10^13`. Простой цикл `for i in range(N): total += i`
в CPython выполняется со скоростью порядка 5 ⋅ 10⁷ итераций в секунду на
ядро — то есть `10^13 / 5⋅10⁷ ≈ 200 000` секунд (≈ 55 часов) даже при
полной утилизации одного ядра, и ≈ 14 часов при честном делении на 4
ядра в multiprocessing. Это не оставляет возможности для серии прогонов.

Поэтому для измеримых замеров взята `N = 10^8` — нагрузка та же по
характеру (CPU-bound, чистая арифметика), но укладывается в секунды.
Параметр выносится в переменную окружения `N`, при желании можно
поднять.

## Реализация

Все три файла лежат в [`Lr_2/task_1/`](https://github.com/cicada-pops/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/HEAD/students/k3340/Yakshin_Artemiy/Lr_2/task_1/).
Каждая программа разбивает `[1, N]` на `WORKERS` равных диапазонов,
запускает их параллельно и собирает частичные суммы.

### threading — `sum_threading.py`

```python
def calculate_sum(start: int, end: int, results: list[int], idx: int) -> None:
    total = 0
    for i in range(start, end + 1):
        total += i
    results[idx] = total


def main() -> None:
    chunk = N // WORKERS
    threads, results = [], [0] * WORKERS
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
```

### multiprocessing — `sum_multiprocessing.py`

```python
def calculate_sum(bounds: tuple[int, int]) -> int:
    start, end = bounds
    total = 0
    for i in range(start, end + 1):
        total += i
    return total


def main() -> None:
    chunk = N // WORKERS
    ranges = [
        (i * chunk + 1, N if i == WORKERS - 1 else (i + 1) * chunk)
        for i in range(WORKERS)
    ]
    t0 = time.perf_counter()
    with Pool(processes=WORKERS) as pool:
        partials = pool.map(calculate_sum, ranges)
    elapsed = time.perf_counter() - t0
```

### asyncio — `sum_async.py`

```python
async def calculate_sum(start: int, end: int) -> int:
    total = 0
    for i in range(start, end + 1):
        total += i
    return total


async def main() -> None:
    chunk = N // WORKERS
    coros = [
        calculate_sum(i * chunk + 1, N if i == WORKERS - 1 else (i + 1) * chunk)
        for i in range(WORKERS)
    ]
    t0 = time.perf_counter()
    partials = await asyncio.gather(*coros)
    elapsed = time.perf_counter() - t0
```

## Результаты замеров

`N = 100 000 000`, `WORKERS = 4`, среднее по нескольким запускам.

| Подход            | Время, с | Ускорение |
|-------------------|---------:|----------:|
| `threading`       | 2.006    | ×1.00     |
| `multiprocessing` | 0.547    | **×3.67** |
| `asyncio`         | 1.850    | ×1.08     |

Все три программы возвращают одинаковую и корректную сумму
`5 000 000 050 000 000` (проверка `assert total == N*(N+1)//2`).

## Анализ

- **Threading** не даёт ускорения, потому что задача чисто CPU-bound:
  GIL не даёт двум потокам исполнять Python-байткод одновременно, и
  четыре потока по очереди делят одно ядро. Накладные расходы на
  переключение между потоками даже немного замедляют по сравнению с
  однопоточной версией.
- **Multiprocessing** даёт реальный параллелизм: каждый процесс — это
  собственный интерпретатор со своим GIL. На 4 ядрах мы получаем
  ускорение, близкое к теоретическому пределу ×4 (×3.67 — небольшая
  потеря на форк процессов и сборку результатов).
- **Asyncio** для CPU-bound задачи бесполезен: цикл событий один,
  внутри `calculate_sum` нет точек `await`, и все четыре корутины
  выполняются строго последовательно. Время практически совпадает с
  однопоточным.

Вывод: для CPU-bound нагрузки правильный выбор — `multiprocessing`.
