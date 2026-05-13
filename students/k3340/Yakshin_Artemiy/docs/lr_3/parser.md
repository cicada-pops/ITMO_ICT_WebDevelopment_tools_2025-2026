# Подзадача 2. Сервис-парсер и синхронный вызов

## Сервис `parser` — отдельное FastAPI-приложение

Логика парсинга вынесена в отдельный микросервис `parser_app`. Он
принимает `POST /parse`, скачивает страницу через `requests`,
извлекает `<title>` через `BeautifulSoup` и пишет результат в БД
`hackathons_db` (таблица `parsed_page`).

```python
@app.post("/parse", response_model=ParseResponse)
def parse(req: ParseRequest) -> ParseResponse:
    url = str(req.url)
    try:
        resp = requests.get(url, timeout=10, headers=HEADERS)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"fetch failed: {e}")

    soup = BeautifulSoup(resp.text, "html.parser")
    title = (soup.title.string or "").strip() if soup.title else "<no-title>"

    with Session(engine) as session:
        row = ParsedPage(url=url, title=title)
        session.add(row)
        session.commit()
        session.refresh(row)

    return ParseResponse(id=row.id, url=row.url, title=row.title)
```

## Модель `ParsedPage` в основной БД

Таблица создаётся параллельно с моделями ЛР1 — обе стороны
(`main_app` и `parser_app`) пишут в одну и ту же `hackathons_db`.

```python
class ParsedPage(SQLModel, table=True):
    __tablename__ = "parsed_page"

    id: Optional[int] = Field(default=None, primary_key=True)
    url: str = Field(index=True)
    title: str
    parsed_at: datetime = Field(default_factory=datetime.utcnow)
```

## Эндпоинт `POST /parse` в основном API

`main_app` не парсит сам — он проксирует запрос в `parser`. Это
оставляет ровно одну реализацию парсера в системе и упрощает
тестирование/замену.

```python
@router.post("", response_model=ParseSyncResponse)
def parse_sync(req: ParseRequest) -> ParseSyncResponse:
    try:
        resp = requests.post(
            f"{settings.PARSER_URL}/parse",
            json={"url": str(req.url)},
            timeout=15,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"parser unavailable: {e}")
    return ParseSyncResponse(**resp.json())
```

`PARSER_URL=http://parser:8001` подставляется через переменную
окружения compose — внутри сети это имя сервиса.

## Эндпоинт `GET /parse` — список последних результатов

Для удобства проверки добавлен ленивый просмотр последних N записей:

```python
@router.get("", response_model=List[ParsedPageRead])
def list_parsed(limit: int = 20, session: Session = Depends(get_session)):
    stmt = select(ParsedPage).order_by(desc(ParsedPage.parsed_at)).limit(limit)
    return session.exec(stmt).all()
```

## Пример вызова

```bash
$ curl -X POST http://localhost:8030/parse \
       -H 'Content-Type: application/json' \
       -d '{"url":"https://example.com/"}'
{"url":"https://example.com/","title":"Example Domain","id":1}

$ curl -X POST http://localhost:8030/parse \
       -H 'Content-Type: application/json' \
       -d '{"url":"https://www.python.org/"}'
{"url":"https://www.python.org/","title":"Welcome to Python.org","id":2}
```

И в БД:

```bash
$ curl http://localhost:8030/parse
[
  {"url":"https://www.python.org/","title":"Welcome to Python.org","id":2,...},
  {"url":"https://example.com/","title":"Example Domain","id":1,...}
]
```
