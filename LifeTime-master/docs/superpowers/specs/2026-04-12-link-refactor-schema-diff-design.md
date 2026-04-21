# Link Module Refactoring + Schema Diff Feature

## Context

Uptime-монитор LifeTime отслеживает доступность сайтов. Ключевая фича — обнаружение изменений в HTML-разметке отслеживаемых страниц. Текущая реализация в `backend/src/modules/link/strategies/` содержит критические баги, нарушает архитектурные конвенции проекта и имеет незавершённую логику сравнения схем.

**Цели:**
1. Привести link-модуль к архитектурным конвенциям проекта (stateless strategies, thin resolver, business logic in service)
2. Реализовать полноценное сравнение HTML-схем с DOM-нормализацией
3. Исправить все найденные баги

## Архитектурные конвенции проекта (для справки)

- **Service** — singleton, вся бизнес-логика, `@staticmethod to_schema/to_model`
- **Resolver** — тонкий слой, только routing + auth через `Depends()`
- **Strategy** — `@staticmethod` методы, без конструктора с зависимостями (как `TokenStrategy`)
- **DI** — module-level singletons, не FastAPI `Depends()` для сервисов
- **DB session** — передаётся как параметр (`AsyncSessionDep`), не создаётся внутри

## Новая структура файлов

```
link/
  strategies/
    __init__.py
    check.py            ← S3-хранение результатов health-check
    schema.py           ← DOM-нормализация, хранение schema.json в S3
  resolver.py           ← тонкий слой: routing + auth
  schema.py             ← Pydantic DTO (+ новые поля для diff)
  service.py            ← вся бизнес-логика (HTTP-проверка, orchestration)
  tasks.py              ← тонкий оркестратор для arq worker
```

## Стратегии

### `strategies/check.py` — `CheckStrategy`

Хранение результатов health-check в S3. `@staticmethod` методы, использует `s3_client` singleton из `lib/s3`.

Методы:
- `save_check(user_id, link_id, check_data)` — сохранить результат проверки в `{user_id}/{link_id}.json`
- `get_checks(user_id, link_id)` — получить историю проверок

Бакет: `link-statistic-bucket-1`. Единый формат S3-ключей (без `user [...]`).

### `strategies/schema.py` — `SchemaStrategy`

DOM-нормализация и хранение schema.json в S3. `@staticmethod` методы.

Методы:
- `normalize_html(raw_html: str) -> str` — нормализация: beautifulsoup4 prettify, удаление `<script>`/`<style>`, сортировка атрибутов, удаление динамических `data-*` атрибутов (nonce, csrf, timestamp)
- `save_snapshot(user_id, link_id, data: dict)` — сохранить schema.json в S3
- `get_snapshot(user_id, link_id) -> dict | None` — получить schema.json из S3
- `compare(old_html: str, new_html: str) -> tuple[list[Change], float]` — вернуть список изменений и change_percentage
- `extract_root_info(html: str) -> tuple[str, dict]` — корневой тег и атрибуты

Бакет: `link-statistic-bucket-1`.

## Формат schema.json в S3

Ключ: `{user_id}/{link_id}/schema.json`

```json
{
  "schema": "<html lang=\"en\">\n  <head>...</head>\n  <body>...</body>\n</html>",
  "different": "<html lang=\"en\">\n  <head>...</head>\n  <body>...</body>\n</html>",
  "tag": "html",
  "attrs": {"lang": "en"},
  "change_percentage": 12.5
}
```

- `schema` — baseline HTML (prettified). Обновляется только по команде пользователя (accept)
- `different` — актуальный HTML с последнего health-check (prettified)
- `tag` / `attrs` — метаданные корневого тега
- `change_percentage` — процент изменённых строк (float 0–100, считается через `difflib.SequenceMatcher.ratio()`)

## Data Flows

### Health-check (фоновая задача, каждые 5 мин)

1. `LinkCheckTask.run()` загружает все ссылки из БД
2. Для каждой ссылки вызывает `link_service.check_link(session, link)`
3. `LinkService.check_link()`:
   - HTTP GET к сайту → raw HTML
   - Формирует check_data (status_code, response_time, ssl_valid, content_length, error)
   - `CheckStrategy.save_check(user_id, link_id, check_data)` → S3
   - `SchemaStrategy.normalize_html(html)` → prettified HTML
   - `SchemaStrategy.get_snapshot(user_id, link_id)` → текущий schema.json
   - Если первый раз: `schema = different = normalized_html`, `change_percentage = 0`
   - Если есть schema.json: сравниваем `schema` (baseline) с новым HTML
   - `SchemaStrategy.save_snapshot(user_id, link_id, updated_data)` → S3

### GET /link/:id (получение ссылки + schema)

1. Resolver → `link_service.retrieve(session, link_id, user_id)`
2. Service: БД-запрос + `SchemaStrategy.get_snapshot(user_id, link_id)`
3. Возвращает `LinkSchemaOut` с полями `schema`, `different`, `tag`, `attrs`, `change_percentage`

### POST /link/:id/schema/accept (принять изменения)

1. Resolver → `link_service.accept_schema(session, link_id, user_id)`
2. Service: `SchemaStrategy.get_snapshot()` → берёт `different` как новый baseline
3. Перезаписывает: `schema = different`, `change_percentage = 0`
4. `SchemaStrategy.save_snapshot()` → S3

### GET /link/:id/schema/:version (версионирование — существующий endpoint)

Оставить как есть, но перенести логику из resolver в service.

## Edge Cases

- **Первый запрос (нет schema.json):** сохраняем HTML как baseline, `different = schema`, `change_percentage = 0`
- **Сайт вернул 500/timeout:** НЕ обновляем `different`, ошибку записываем в check_data
- **S3 недоступен:** логируем, пропускаем сравнение, не ломаем health-check
- **HTML > 5MB:** обрезаем, добавляем `truncated: true` в schema.json
- **Динамический контент:** нормализация убирает `<script>`, `<style>`, сортирует атрибуты, удаляет `data-*` с динамическими значениями

## Баги для исправления

1. `LinkCheckStrategy()` без `s3_client` — singleton crash при импорте
2. `get_snapshot()` без `await` в service.py:97
3. Несовпадение S3-ключей: `save_check` vs `get_checks`
4. `LinkModel` не импортирован в resolver.py
5. Опечатка `stategies` → `strategies`
6. Прямой доступ к S3/ORM в resolver (бизнес-логика утекла)

## Новая зависимость

- `beautifulsoup4` — для парсинга и нормализации HTML (prettify, удаление тегов, сортировка атрибутов)

## Фронтенд-интеграция

Фронт использует `react-diff-viewer-continued`. Бэкенд отдаёт `schema` (oldValue) и `different` (newValue) как prettified HTML-строки. Фронт рендерит unified/split diff view.
