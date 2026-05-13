# Задача 2. Параллельный парсинг с сохранением в БД

## Постановка

Реализовать три программы (`threading`, `multiprocessing`, `asyncio`),
которые параллельно парсят список URL, извлекают `<title>` страницы и
сохраняют его в БД из ЛР1 (`hackathons_db`).

## Схема БД

В базу ЛР1 добавлена служебная таблица `parsed_page`:

```python
class ParsedPage(SQLModel, table=True):
    __tablename__ = "parsed_page"

    id: Optional[int] = Field(default=None, primary_key=True)
    url: str = Field(index=True)
    title: str
    parsed_at: datetime = Field(default_factory=datetime.utcnow)
```

Существующие таблицы ЛР1 (`location`, `hackathon`, `team`, ...) не
изменяются — мы лишь дописываем рядом новую сущность через
`SQLModel.metadata.create_all`. Это позволяет переиспользовать ту же
PostgreSQL-инстанцию и `.env`, что и в ЛР1.

## Список URL

12 страниц, репрезентативных для эксперимента: главные страницы фреймворков,
документация Python по `threading`/`multiprocessing`/`asyncio`, страницы
Википедии. На каждой из них берётся текст внутри тега `<title>`.

```python
URLS = [
    "https://example.com/",
    "https://www.python.org/",
    "https://docs.python.org/3/library/asyncio.html",
    "https://docs.python.org/3/library/threading.html",
    "https://docs.python.org/3/library/multiprocessing.html",
    "https://fastapi.tiangolo.com/",
    "https://sqlmodel.tiangolo.com/",
    "https://www.postgresql.org/",
    "https://en.wikipedia.org/wiki/Hackathon",
    "https://en.wikipedia.org/wiki/Concurrency_(computer_science)",
    "https://en.wikipedia.org/wiki/Thread_(computing)",
    "https://en.wikipedia.org/wiki/Process_(computing)",
]
```

## Реализации

### threading — `parse_threading.py`

```python
def parse_and_save(url: str) -> None:
    try:
        resp = requests.get(url, timeout=10, headers=HEADERS)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        title = (soup.title.string or "").strip() if soup.title else "<no-title>"
    except Exception as e:
        title = f"<error: {e.__class__.__name__}>"
    save_title(url, title)


def main() -> None:
    init_db()
    threads = [threading.Thread(target=parse_and_save, args=(u,)) for u in URLS]
    for t in threads: t.start()
    for t in threads: t.join()
```

### multiprocessing — `parse_multiprocessing.py`

```python
def parse_and_save(url: str) -> str:
    resp = requests.get(url, timeout=10, headers=HEADERS)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    title = (soup.title.string or "").strip() if soup.title else "<no-title>"
    save_title(url, title)
    return title


def main() -> None:
    init_db()
    with Pool(processes=min(8, len(URLS))) as pool:
        pool.map(parse_and_save, URLS)
```

### asyncio + aiohttp — `parse_async.py`

```python
async def parse_and_save(session: aiohttp.ClientSession, url: str) -> tuple[str, str]:
    async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
        resp.raise_for_status()
        html = await resp.text()
    soup = BeautifulSoup(html, "html.parser")
    title = (soup.title.string or "").strip() if soup.title else "<no-title>"
    return url, title


async def main() -> None:
    init_db()
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        rows = await asyncio.gather(*(parse_and_save(session, u) for u in URLS))
    save_titles_bulk(list(rows))
```

В асинхронной версии запись в БД сделана пачкой одной транзакцией:
`psycopg2` не умеет асинхронные коммиты, поэтому держать в каждой
корутине отдельную блокирующую сессию было бы дороже, чем собрать
заголовки и сохранить их в конце.

## Результаты замеров

12 URL, среднее по нескольким прогонам.

| Подход                                  | Время, с | Ускорение vs threading |
|-----------------------------------------|---------:|-----------------------:|
| `threading` (12 потоков)                | 0.706    | ×1.00                  |
| `multiprocessing` (Pool, 8 процессов)   | 1.190    | ×0.59 (медленнее)      |
| `asyncio + aiohttp`                     | 0.741    | ×0.95                  |

## Анализ

- **Threading** для I/O-bound задач работает почти так же хорошо, как
  asyncio: при системном вызове `recv()` GIL отпускается, и другие
  потоки получают возможность работать. На 12 URL мы упираемся в время
  ответа самого медленного сервера, а не в CPU.
- **Multiprocessing** заметно медленнее из-за накладных расходов на
  старт пула процессов (fork + bootstrap интерпретатора + сериализация
  аргументов через pickle). Для коротких I/O-bound задач этот оверхед
  превышает выгоду от параллелизма.
- **Asyncio** + `aiohttp` показывает результат, сравнимый с threading,
  но намного дешевле по ресурсам: одна нить, одна память,
  переключение задач в user-space. Если бы URL было 100, разрыв в
  пользу asyncio был бы заметнее.

Вывод: для I/O-bound задач (сеть, диск, БД) `multiprocessing` —
неоптимальный выбор; разумно использовать `threading` или, лучше,
`asyncio` — особенно при большом количестве одновременных операций.
