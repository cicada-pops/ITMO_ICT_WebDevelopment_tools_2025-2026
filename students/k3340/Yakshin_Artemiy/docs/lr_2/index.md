# Лабораторная работа №2 — Потоки, процессы, асинхронность

## Цель работы

Понять отличия между `threading`, `multiprocessing` и `asyncio` в Python,
получить практический опыт измерения и сравнения времени выполнения
параллельных программ на CPU-bound и I/O-bound задачах.

## Структура отчёта

| # | Задача | Страница |
|---|--------|----------|
| 1 | Подсчёт суммы 1..N тремя подходами | [task_1](task_1.md) |
| 2 | Параллельный парсинг и сохранение в БД | [task_2.md](task_2.md) |
| — | Сводное сравнение и выводы | [summary](summary.md) |

## Ссылки на исходный код

- Задача 1 — [`Lr_2/task_1/`](https://github.com/cicada-pops/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/HEAD/students/k3340/Yakshin_Artemiy/Lr_2/task_1/)
- Задача 2 — [`Lr_2/task_2/`](https://github.com/cicada-pops/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/HEAD/students/k3340/Yakshin_Artemiy/Lr_2/task_2/)

## Окружение запуска

| Параметр | Значение |
|---|---|
| OS | macOS (darwin 25.2) |
| CPU | Apple Silicon (8 ядер) |
| Python | 3.9.6 |
| PostgreSQL | используется БД `hackathons_db` из ЛР1 |

Все замеры сделаны при `WORKERS=4` и `N=10^8` для задачи 1 и при списке
из 12 URL для задачи 2.
