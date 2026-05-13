# Задача 2. Параллельный парсинг с сохранением в БД

Парсим список URL, забираем `<title>`, сохраняем в таблицу
`parsed_page` базы `hackathons_db` из ЛР1.

## Запуск

```bash
# из директории Lr_2
python -m task_2.parse_threading
python -m task_2.parse_multiprocessing
python -m task_2.parse_async
# или все три подряд:
python -m task_2.benchmark
```

`.env` ожидает `DB_ADMIN=postgresql://...`. По умолчанию это та же БД,
что у `lab_1` (`hackathons_db`).

## Таблица БД

```python
class ParsedPage(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    url: str
    title: str
    parsed_at: datetime
```

## Подходы

| Файл                          | Подход                | I/O-bound подходит? |
|-------------------------------|-----------------------|---------------------|
| `parse_threading.py`          | `threading + requests` | Да: GIL отпускается на сетевой I/O |
| `parse_multiprocessing.py`    | `multiprocessing + requests` | Работает, но накладные расходы на форк процессов высокие |
| `parse_async.py`              | `asyncio + aiohttp`   | Да: самое дешёвое переключение между задачами |
