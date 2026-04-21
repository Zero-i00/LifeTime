# Link Module Refactoring + Schema Diff Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Привести `link/` модуль к архитектурным конвенциям проекта, исправить все баги и реализовать HTML schema diff с prettified old/new HTML для react-diff-viewer-continued на фронте.

**Architecture:** `CheckStrategy` и `SchemaStrategy` — stateless классы с `@staticmethod` методами (как `TokenStrategy`), использующие `s3_client` singleton напрямую. `LinkService` содержит всю бизнес-логику включая HTTP-проверку сайтов. `LinkCheckTask` — тонкий оркестратор без бизнес-логики. `LinkResolver` — тонкий слой только для routing + auth.

**Tech Stack:** Python/FastAPI, SQLAlchemy (async), aiobotocore (S3), aiohttp, beautifulsoup4, difflib (stdlib), arq (worker), pytest + pytest-asyncio

---

## File Map

| Файл | Действие | Ответственность |
|------|----------|-----------------|
| `backend/src/modules/link/strategies/check.py` | Rewrite | Stateless S3-хранение check results |
| `backend/src/modules/link/strategies/schema.py` | Create | HTML нормализация + S3-хранение schema.json |
| `backend/src/modules/link/strategies/__init__.py` | Update | Экспорт `check_strategy`, `schema_strategy` |
| `backend/src/modules/link/schema.py` | Update | Новые поля в `LinkSchemaOut` |
| `backend/src/modules/link/service.py` | Rewrite | Вся бизнес-логика: CRUD + check_link + accept_schema |
| `backend/src/modules/link/resolver.py` | Rewrite | Thin layer: routing + auth, добавить accept endpoint |
| `backend/src/modules/link/tasks.py` | Rewrite | Thin orchestrator: только загрузка links + семафор |
| `backend/tests/modules/link/strategies/test_schema.py` | Create | Unit тесты SchemaStrategy |
| `backend/tests/modules/link/strategies/test_check.py` | Create | Unit тесты CheckStrategy |
| `backend/pyproject.toml` | Update | Добавить beautifulsoup4 |

---

### Task 1: Добавить beautifulsoup4 и создать тест-инфраструктуру

**Files:**
- Modify: `backend/pyproject.toml`
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/modules/__init__.py`
- Create: `backend/tests/modules/link/__init__.py`
- Create: `backend/tests/modules/link/strategies/__init__.py`

- [ ] **Step 1: Установить beautifulsoup4**

```bash
cd /path/to/backend
uv add beautifulsoup4
```

Expected output: `Resolved ... added beautifulsoup4` в stdout.

- [ ] **Step 2: Проверить что beautifulsoup4 появился в pyproject.toml**

В `backend/pyproject.toml` в секции `dependencies` должна появиться строка:
```
"beautifulsoup4>=4.12",
```

- [ ] **Step 3: Создать __init__.py файлы для тестов**

```bash
mkdir -p backend/tests/modules/link/strategies
touch backend/tests/__init__.py
touch backend/tests/modules/__init__.py
touch backend/tests/modules/link/__init__.py
touch backend/tests/modules/link/strategies/__init__.py
```

- [ ] **Step 4: Проверить что pytest находит тесты**

```bash
cd backend
pytest tests/ --collect-only
```

Expected: `no tests ran` (без ошибок, просто пусто — тесты ещё не написаны).

- [ ] **Step 5: Commit**

```bash
git add backend/pyproject.toml backend/tests/
git commit -m "chore: add beautifulsoup4, create test directory structure"
```

---

### Task 2: Переписать CheckStrategy (stateless, исправить S3-ключ)

**Files:**
- Rewrite: `backend/src/modules/link/strategies/check.py`
- Create: `backend/tests/modules/link/strategies/test_check.py`

- [ ] **Step 1: Написать падающие тесты для CheckStrategy**

Создать `backend/tests/modules/link/strategies/test_check.py`:

```python
import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.asyncio
async def test_save_check_uses_correct_key():
    """save_check должен писать в {user_id}/{link_id}.json (без 'user [...]')"""
    mock_s3 = AsyncMock()
    mock_s3.get_object = AsyncMock(return_value=None)
    mock_s3.put_object = AsyncMock()

    with patch("modules.link.strategies.check.s3_client", mock_s3):
        from modules.link.strategies.check import CheckStrategy
        await CheckStrategy.save_check(1, 42, {"status_code": 200})

    mock_s3.put_object.assert_called_once()
    call_args = mock_s3.put_object.call_args
    assert call_args[0][1] == "1/42.json"  # key без "user [...]"


@pytest.mark.asyncio
async def test_save_check_appends_to_existing():
    """save_check должен добавлять к существующему массиву"""
    existing = json.dumps([{"status_code": 200}]).encode()
    mock_s3 = AsyncMock()
    mock_s3.get_object = AsyncMock(return_value=existing)
    mock_s3.put_object = AsyncMock()

    with patch("modules.link.strategies.check.s3_client", mock_s3):
        from modules.link.strategies.check import CheckStrategy
        await CheckStrategy.save_check(1, 42, {"status_code": 503})

    call_args = mock_s3.put_object.call_args
    saved = json.loads(call_args[0][2])
    assert len(saved) == 2
    assert saved[1]["status_code"] == 503


@pytest.mark.asyncio
async def test_get_checks_uses_same_key_as_save():
    """get_checks должен читать из того же ключа что и save_check"""
    data = json.dumps([{"status_code": 200}]).encode()
    mock_s3 = AsyncMock()
    mock_s3.get_object = AsyncMock(return_value=data)

    with patch("modules.link.strategies.check.s3_client", mock_s3):
        from modules.link.strategies.check import CheckStrategy
        result = await CheckStrategy.get_checks(1, 42)

    mock_s3.get_object.assert_called_once_with("link-statistic-bucket-1", "1/42.json")
    assert result == [{"status_code": 200}]


@pytest.mark.asyncio
async def test_get_checks_returns_empty_list_when_no_data():
    mock_s3 = AsyncMock()
    mock_s3.get_object = AsyncMock(return_value=None)

    with patch("modules.link.strategies.check.s3_client", mock_s3):
        from modules.link.strategies.check import CheckStrategy
        result = await CheckStrategy.get_checks(1, 42)

    assert result == []
```

- [ ] **Step 2: Запустить тесты — убедиться что падают**

```bash
cd backend
pytest tests/modules/link/strategies/test_check.py -v
```

Expected: FAIL — `ImportError` или `AssertionError` (старый код использует конструктор с `s3_client`).

- [ ] **Step 3: Переписать check.py как stateless**

Полностью заменить `backend/src/modules/link/strategies/check.py`:

```python
import json

from lib.s3 import s3_client

LINK_STATISTIC_BUCKET = "link-statistic-bucket-1"


class CheckStrategy:
    @staticmethod
    async def save_check(user_id: int, link_id: int, check_data: dict) -> None:
        key = f"{user_id}/{link_id}.json"
        existing = await s3_client.get_object(LINK_STATISTIC_BUCKET, key)
        checks = json.loads(existing) if existing else []
        checks.append(check_data)
        await s3_client.put_object(LINK_STATISTIC_BUCKET, key, json.dumps(checks).encode())

    @staticmethod
    async def get_checks(user_id: int, link_id: int) -> list[dict]:
        key = f"{user_id}/{link_id}.json"
        existing = await s3_client.get_object(LINK_STATISTIC_BUCKET, key)
        return json.loads(existing) if existing else []


check_strategy = CheckStrategy()
```

- [ ] **Step 4: Запустить тесты — убедиться что проходят**

```bash
cd backend
pytest tests/modules/link/strategies/test_check.py -v
```

Expected: `4 passed`.

- [ ] **Step 5: Commit**

```bash
git add backend/src/modules/link/strategies/check.py \
        backend/tests/modules/link/strategies/test_check.py
git commit -m "refactor: CheckStrategy to stateless, fix S3 key format"
```

---

### Task 3: Создать SchemaStrategy (нормализация HTML + S3)

**Files:**
- Create: `backend/src/modules/link/strategies/schema.py`
- Create: `backend/tests/modules/link/strategies/test_schema.py`

- [ ] **Step 1: Написать падающие тесты**

Создать `backend/tests/modules/link/strategies/test_schema.py`:

```python
import json
import pytest
from unittest.mock import AsyncMock, patch


# --- normalize_html тесты ---

def test_normalize_html_removes_script_tags():
    from modules.link.strategies.schema import SchemaStrategy
    html = "<html><body><script>alert(1)</script><p>Hello</p></body></html>"
    result = SchemaStrategy.normalize_html(html)
    assert "<script>" not in result
    assert "Hello" in result


def test_normalize_html_removes_style_tags():
    from modules.link.strategies.schema import SchemaStrategy
    html = "<html><head><style>body{color:red}</style></head><body><p>Hi</p></body></html>"
    result = SchemaStrategy.normalize_html(html)
    assert "<style>" not in result
    assert "Hi" in result


def test_normalize_html_sorts_attributes():
    from modules.link.strategies.schema import SchemaStrategy
    html = '<html><body><div z-attr="1" a-attr="2">text</div></body></html>'
    result = SchemaStrategy.normalize_html(html)
    # z-attr должен идти после a-attr
    a_pos = result.find("a-attr")
    z_pos = result.find("z-attr")
    assert a_pos < z_pos


def test_normalize_html_removes_dynamic_attrs():
    from modules.link.strategies.schema import SchemaStrategy
    html = '<html><body><form data-csrf-token="abc123" class="form">text</form></body></html>'
    result = SchemaStrategy.normalize_html(html)
    assert "abc123" not in result
    assert "form" in result  # class должен остаться


def test_normalize_html_returns_prettified_string():
    from modules.link.strategies.schema import SchemaStrategy
    html = "<html><body><p>Test</p></body></html>"
    result = SchemaStrategy.normalize_html(html)
    assert isinstance(result, str)
    assert "\n" in result  # prettified содержит переносы строк


# --- extract_root_info тесты ---

def test_extract_root_info_html():
    from modules.link.strategies.schema import SchemaStrategy
    html = '<html lang="en"><body></body></html>'
    tag, attrs = SchemaStrategy.extract_root_info(html)
    assert tag == "html"
    assert attrs.get("lang") == "en"


# --- compute_change_percentage тесты ---

def test_compute_change_percentage_identical():
    from modules.link.strategies.schema import SchemaStrategy
    html = "<html><body><p>Hello</p></body></html>"
    result = SchemaStrategy.compute_change_percentage(html, html)
    assert result == 0.0


def test_compute_change_percentage_different():
    from modules.link.strategies.schema import SchemaStrategy
    old = "<html><body><p>Hello</p></body></html>"
    new = "<html><body><p>World</p><section>New</section></body></html>"
    result = SchemaStrategy.compute_change_percentage(old, new)
    assert 0 < result <= 100


def test_compute_change_percentage_returns_float():
    from modules.link.strategies.schema import SchemaStrategy
    result = SchemaStrategy.compute_change_percentage("abc", "xyz")
    assert isinstance(result, float)


# --- save_snapshot / get_snapshot тесты ---

@pytest.mark.asyncio
async def test_save_snapshot_uses_correct_key():
    mock_s3 = AsyncMock()
    mock_s3.put_object = AsyncMock()

    with patch("modules.link.strategies.schema.s3_client", mock_s3):
        from modules.link.strategies.schema import SchemaStrategy
        data = {"schema": "<html/>", "different": "<html/>", "tag": "html", "attrs": {}, "change_percentage": 0.0}
        await SchemaStrategy.save_snapshot(1, 42, data)

    mock_s3.put_object.assert_called_once()
    call_args = mock_s3.put_object.call_args
    assert call_args[0][1] == "1/42/schema.json"


@pytest.mark.asyncio
async def test_get_snapshot_returns_dict():
    data = {"schema": "<html/>", "different": "<html/>", "tag": "html", "attrs": {}, "change_percentage": 0.0}
    mock_s3 = AsyncMock()
    mock_s3.get_object = AsyncMock(return_value=json.dumps(data).encode())

    with patch("modules.link.strategies.schema.s3_client", mock_s3):
        from modules.link.strategies.schema import SchemaStrategy
        result = await SchemaStrategy.get_snapshot(1, 42)

    assert result == data


@pytest.mark.asyncio
async def test_get_snapshot_returns_none_when_missing():
    mock_s3 = AsyncMock()
    mock_s3.get_object = AsyncMock(return_value=None)

    with patch("modules.link.strategies.schema.s3_client", mock_s3):
        from modules.link.strategies.schema import SchemaStrategy
        result = await SchemaStrategy.get_snapshot(1, 42)

    assert result is None
```

- [ ] **Step 2: Запустить тесты — убедиться что падают**

```bash
cd backend
pytest tests/modules/link/strategies/test_schema.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'modules.link.strategies.schema'`.

- [ ] **Step 3: Создать schema.py**

Создать `backend/src/modules/link/strategies/schema.py`:

```python
import difflib
import json
import re
from typing import Optional

from bs4 import BeautifulSoup

from lib.s3 import s3_client

LINK_STATISTIC_BUCKET = "link-statistic-bucket-1"
MAX_HTML_BYTES = 5 * 1024 * 1024  # 5MB

_DYNAMIC_ATTR = re.compile(r"(nonce|csrf|token|timestamp|_ga|captcha)", re.IGNORECASE)


class SchemaStrategy:
    @staticmethod
    def normalize_html(raw_html: str) -> str:
        """Нормализует HTML: prettify + удаляет script/style + сортирует атрибуты."""
        if len(raw_html.encode("utf-8", errors="replace")) > MAX_HTML_BYTES:
            raw_html = raw_html[:MAX_HTML_BYTES]

        soup = BeautifulSoup(raw_html, "html.parser")

        for tag in soup.find_all(["script", "style"]):
            tag.decompose()

        for tag in soup.find_all(True):
            if tag.attrs:
                cleaned = {
                    k: v
                    for k, v in sorted(tag.attrs.items())
                    if not _DYNAMIC_ATTR.search(k)
                }
                tag.attrs = cleaned

        return soup.prettify()

    @staticmethod
    def extract_root_info(html: str) -> tuple[str, dict]:
        """Возвращает имя и атрибуты корневого тега."""
        soup = BeautifulSoup(html, "html.parser")
        root = soup.find()
        if root is None:
            return "html", {}
        return root.name, dict(root.attrs)

    @staticmethod
    def compute_change_percentage(old: str, new: str) -> float:
        """Процент изменений (0.0 – 100.0) через difflib."""
        if old == new:
            return 0.0
        ratio = difflib.SequenceMatcher(None, old, new).ratio()
        return round((1.0 - ratio) * 100, 2)

    @staticmethod
    async def save_snapshot(user_id: int, link_id: int, data: dict) -> None:
        """Сохраняет schema.json в S3."""
        key = f"{user_id}/{link_id}/schema.json"
        await s3_client.put_object(
            LINK_STATISTIC_BUCKET, key, json.dumps(data).encode()
        )

    @staticmethod
    async def get_snapshot(user_id: int, link_id: int) -> Optional[dict]:
        """Получает schema.json из S3, или None если файл не найден."""
        key = f"{user_id}/{link_id}/schema.json"
        data = await s3_client.get_object(LINK_STATISTIC_BUCKET, key)
        if data is None:
            return None
        return json.loads(data)


schema_strategy = SchemaStrategy()
```

- [ ] **Step 4: Запустить тесты — убедиться что проходят**

```bash
cd backend
pytest tests/modules/link/strategies/test_schema.py -v
```

Expected: `11 passed`.

- [ ] **Step 5: Commit**

```bash
git add backend/src/modules/link/strategies/schema.py \
        backend/tests/modules/link/strategies/test_schema.py
git commit -m "feat: add SchemaStrategy with HTML normalization and S3 persistence"
```

---

### Task 4: Обновить __init__.py стратегий и LinkSchemaOut DTO

**Files:**
- Update: `backend/src/modules/link/strategies/__init__.py`
- Update: `backend/src/modules/link/schema.py`

- [ ] **Step 1: Обновить __init__.py стратегий**

Заменить содержимое `backend/src/modules/link/strategies/__init__.py`:

```python
from modules.link.strategies.check import check_strategy
from modules.link.strategies.schema import schema_strategy

__all__ = ["check_strategy", "schema_strategy"]
```

- [ ] **Step 2: Обновить LinkSchemaOut в schema.py**

Заменить содержимое `backend/src/modules/link/schema.py`:

```python
import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class LinkSchemaIn(BaseModel):
    url: str
    project_id: int


class LinkSchemaUpdate(BaseModel):
    url: Optional[str] = None


class LinkSchemaFilter(BaseModel):
    url: Optional[str] = None
    project_id: Optional[int] = None
    user_id: Optional[int] = None


class LinkSchemaOut(BaseModel):
    id: int
    url: str
    project_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    schema: Optional[str] = None
    different: Optional[str] = None
    tag: Optional[str] = None
    attrs: Optional[dict] = None
    change_percentage: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)
```

- [ ] **Step 3: Проверить что старые тесты ещё проходят**

```bash
cd backend
pytest tests/ -v
```

Expected: все предыдущие тесты (`test_check.py`, `test_schema.py`) — PASS.

- [ ] **Step 4: Commit**

```bash
git add backend/src/modules/link/strategies/__init__.py \
        backend/src/modules/link/schema.py
git commit -m "feat: export strategy singletons, add schema fields to LinkSchemaOut"
```

---

### Task 5: Переписать service.py — бизнес-логика, check_link, accept_schema

**Files:**
- Rewrite: `backend/src/modules/link/service.py`

Текущее состояние: `get_link_schema` не имеет `await`, использует сломанный singleton `link_check_stategies`, утекает S3-логика в resolver.

- [ ] **Step 1: Полностью заменить service.py**

```python
import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Optional, Sequence

import aiohttp
from aiohttp import ClientConnectorError, ClientSSLError, ServerTimeoutError
from fastapi import status, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import IS_DEBUG, settings
from database.models import LinkModel, ProjectModel
from lib.s3 import s3_client
from modules.link.schema import LinkSchemaOut, LinkSchemaIn, LinkSchemaUpdate, LinkSchemaFilter
from modules.link.strategies.check import CheckStrategy
from modules.link.strategies.schema import SchemaStrategy

logger = logging.getLogger(__name__)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _error_result(elapsed_ms: int, ssl_valid: Optional[bool], error: Exception) -> dict:
    return {
        "status_code": None,
        "response_time_ms": elapsed_ms,
        "is_up": False,
        "checked_at": _now(),
        "ssl_valid": ssl_valid,
        "content_length": None,
        "error_message": str(error),
    }


class LinkService:
    def __init__(self):
        self.not_found_exception = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found",
        )

    async def list(
        self, session: AsyncSession, filters: LinkSchemaFilter
    ) -> Sequence[LinkModel]:
        query = select(LinkModel)

        if filters.url is not None:
            query = query.where(LinkModel.url.ilike(f"%{filters.url}%"))
        if filters.project_id is not None:
            query = query.where(LinkModel.project_id == filters.project_id)
        if filters.user_id is not None:
            query = query.join(LinkModel.project).where(
                ProjectModel.user_id == filters.user_id
            )

        result = await session.execute(query)
        return result.scalars().all()

    async def retrieve(
        self, session: AsyncSession, link_id: int, filters: LinkSchemaFilter
    ) -> LinkModel:
        link = await session.get(LinkModel, link_id)
        if link is None:
            raise self.not_found_exception
        if filters.user_id is not None and link.project.user_id != filters.user_id:
            raise self.not_found_exception
        return link

    async def retrieve_with_schema(
        self, session: AsyncSession, link_id: int, filters: LinkSchemaFilter
    ) -> LinkSchemaOut:
        """Возвращает ссылку вместе с данными schema.json из S3."""
        link = await self.retrieve(session, link_id, filters)
        schema_data = await SchemaStrategy.get_snapshot(link.project.user_id, link_id)
        return self.to_schema(link, schema_data)

    async def create(
        self, session: AsyncSession, user_id: int, obj: LinkSchemaIn
    ) -> LinkModel:
        project = await session.get(ProjectModel, obj.project_id)
        if project is None or project.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        link = LinkModel(url=obj.url, project_id=obj.project_id)
        session.add(link)
        await session.commit()
        await session.refresh(link)
        return link

    async def update(
        self,
        session: AsyncSession,
        link_id: int,
        user_id: int,
        obj: LinkSchemaUpdate,
    ) -> LinkModel:
        link = await session.get(LinkModel, link_id)
        if link is None or link.project.user_id != user_id:
            raise self.not_found_exception

        if obj.url is not None:
            link.url = obj.url

        await session.commit()
        await session.refresh(link)
        return link

    async def delete(
        self, session: AsyncSession, link_id: int, user_id: int
    ) -> None:
        link = await session.get(LinkModel, link_id)
        if link is None or link.project.user_id != user_id:
            raise self.not_found_exception

        await session.delete(link)
        await session.commit()

    async def accept_schema(
        self, session: AsyncSession, link_id: int, user_id: int
    ) -> None:
        """Принимает изменения: текущий different становится новым baseline."""
        link = await session.get(LinkModel, link_id)
        if link is None or link.project.user_id != user_id:
            raise self.not_found_exception

        snapshot = await SchemaStrategy.get_snapshot(user_id, link_id)
        if snapshot is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Schema not found",
            )

        new_baseline = snapshot["different"]
        tag, attrs = SchemaStrategy.extract_root_info(new_baseline)

        await SchemaStrategy.save_snapshot(
            user_id,
            link_id,
            {
                "schema": new_baseline,
                "different": new_baseline,
                "tag": tag,
                "attrs": attrs,
                "change_percentage": 0.0,
            },
        )

    async def get_schema_version(
        self,
        session: AsyncSession,
        link_id: int,
        user_id: int,
        version: str,
    ) -> dict:
        """Получает версионированную схему из бакета link-schemas."""
        link = await session.get(LinkModel, link_id)
        if link is None or link.project.user_id != user_id:
            raise self.not_found_exception

        key = f"{user_id}/{link_id}/schemas/schema_{version}.json"
        data = await s3_client.get_object("link-schemas", key)

        if data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Schema version {version} not found",
            )

        try:
            return json.loads(data)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid JSON format in schema file",
            )

    async def check_link(
        self,
        link: LinkModel,
        http_session: aiohttp.ClientSession,
        timeout: int,
    ) -> None:
        """Выполняет health-check ссылки: HTTP запрос + запись в S3."""
        url = link.url
        user_id = link.project.user_id
        link_id = link.id
        is_https = url.startswith("https://")
        loop = asyncio.get_running_loop()
        start = loop.time()

        def elapsed() -> int:
            return int((loop.time() - start) * 1000)

        html: Optional[str] = None
        check_data: dict

        try:
            async with http_session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=timeout),
                allow_redirects=True,
                ssl=True,
            ) as resp:
                raw = await resp.read()
                content_length = len(raw)
                is_up = 200 <= resp.status < 400
                check_data = {
                    "status_code": resp.status,
                    "response_time_ms": elapsed(),
                    "is_up": is_up,
                    "checked_at": _now(),
                    "ssl_valid": True if is_https else None,
                    "content_length": content_length,
                    "error_message": None,
                }
                if is_up:
                    html = raw.decode("utf-8", errors="replace")
        except ClientSSLError as e:
            check_data = _error_result(elapsed(), ssl_valid=False, error=e)
        except (ClientConnectorError, ServerTimeoutError, asyncio.TimeoutError) as e:
            check_data = _error_result(elapsed(), ssl_valid=None, error=e)
        except Exception as e:
            check_data = _error_result(elapsed(), ssl_valid=None, error=e)

        if not IS_DEBUG:
            await CheckStrategy.save_check(user_id, link_id, check_data)

        if html is not None:
            await self._update_schema(user_id, link_id, html)

    async def _update_schema(
        self, user_id: int, link_id: int, html: str
    ) -> None:
        """Нормализует HTML и обновляет schema.json в S3."""
        try:
            normalized = SchemaStrategy.normalize_html(html)
            existing = await SchemaStrategy.get_snapshot(user_id, link_id)
            tag, attrs = SchemaStrategy.extract_root_info(normalized)

            if existing is None:
                await SchemaStrategy.save_snapshot(
                    user_id,
                    link_id,
                    {
                        "schema": normalized,
                        "different": normalized,
                        "tag": tag,
                        "attrs": attrs,
                        "change_percentage": 0.0,
                    },
                )
                return

            baseline = existing["schema"]
            percentage = SchemaStrategy.compute_change_percentage(baseline, normalized)

            await SchemaStrategy.save_snapshot(
                user_id,
                link_id,
                {
                    "schema": baseline,
                    "different": normalized,
                    "tag": tag,
                    "attrs": attrs,
                    "change_percentage": percentage,
                },
            )
        except Exception as exc:
            logger.warning(
                "Failed to update schema for link %s (user %s): %s",
                link_id,
                user_id,
                exc,
            )

    @staticmethod
    def to_schema(
        obj: LinkModel, schema_data: Optional[dict] = None
    ) -> LinkSchemaOut:
        return LinkSchemaOut(
            id=obj.id,
            url=obj.url,
            project_id=obj.project_id,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            schema=schema_data.get("schema") if schema_data else None,
            different=schema_data.get("different") if schema_data else None,
            tag=schema_data.get("tag") if schema_data else None,
            attrs=schema_data.get("attrs") if schema_data else None,
            change_percentage=schema_data.get("change_percentage") if schema_data else None,
        )


link_service = LinkService()
```

- [ ] **Step 2: Запустить все тесты**

```bash
cd backend
pytest tests/ -v
```

Expected: все тесты из Task 2 и Task 3 — PASS. Ошибок импорта нет.

- [ ] **Step 3: Commit**

```bash
git add backend/src/modules/link/service.py
git commit -m "refactor: LinkService — move all business logic, add check_link and accept_schema"
```

---

### Task 6: Переписать tasks.py — тонкий оркестратор

**Files:**
- Rewrite: `backend/src/modules/link/tasks.py`

- [ ] **Step 1: Заменить tasks.py**

```python
import asyncio
import logging
from typing import Any

import aiohttp
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from config import settings
from database.models.link import LinkModel
from database.session import session_factory
from modules.link.service import link_service

logger = logging.getLogger(__name__)


class LinkCheckTask:
    async def run(self, ctx: dict[str, Any]) -> None:
        logger.info("Starting link health check run")

        semaphore = asyncio.Semaphore(settings.worker.max_concurrent_checks)
        timeout = settings.worker.request_timeout_seconds

        async with session_factory() as session:
            result = await session.execute(
                select(LinkModel).options(joinedload(LinkModel.project))
            )
            links = result.scalars().all()

        if not links:
            logger.info("No links to check")
            return

        logger.info(f"Checking {len(links)} links")

        async with aiohttp.ClientSession() as http_session:
            async def check_and_log(link: LinkModel) -> None:
                async with semaphore:
                    await link_service.check_link(link, http_session, timeout)
                    logger.info(f"Link {link.id} ({link.url}): checked")

            await asyncio.gather(*[check_and_log(link) for link in links])

        logger.info("Link health check run complete")
```

- [ ] **Step 2: Запустить все тесты**

```bash
cd backend
pytest tests/ -v
```

Expected: все предыдущие тесты — PASS.

- [ ] **Step 3: Commit**

```bash
git add backend/src/modules/link/tasks.py
git commit -m "refactor: LinkCheckTask to thin orchestrator, delegate logic to LinkService"
```

---

### Task 7: Переписать resolver.py — тонкий слой + новый endpoint

**Files:**
- Rewrite: `backend/src/modules/link/resolver.py`

Текущие проблемы: `get_link_schema_version` имеет S3/ORM логику прямо в resolver, `LinkModel` не импортирован, дублируется логика.

- [ ] **Step 1: Заменить resolver.py**

```python
from typing import List, Optional

from fastapi import APIRouter, status, Depends, Query

from database.models.user import UserRole
from database.session import AsyncSessionDep
from modules.auth.schema import AccessTokenPayload
from modules.auth.service import auth_service
from modules.link.schema import LinkSchemaOut, LinkSchemaIn, LinkSchemaUpdate, LinkSchemaFilter
from modules.link.service import link_service


class LinkResolver:
    router = APIRouter(
        prefix="/link",
        tags=["Link"],
    )

    @staticmethod
    @router.get("/", status_code=status.HTTP_200_OK)
    async def list(
        session: AsyncSessionDep,
        url: Optional[str] = Query(None),
        project_id: Optional[int] = Query(None),
        credentials: AccessTokenPayload = Depends(auth_service.get_access_token_payload),
    ) -> List[LinkSchemaOut]:
        is_admin = credentials.role == UserRole.ADMIN.value
        filters = LinkSchemaFilter(
            url=url,
            project_id=project_id,
            user_id=None if is_admin else credentials.user_id,
        )
        links = await link_service.list(session, filters)
        return [link_service.to_schema(link) for link in links]

    @staticmethod
    @router.get("/{link_id}", status_code=status.HTTP_200_OK)
    async def retrieve(
        session: AsyncSessionDep,
        link_id: int,
        credentials: AccessTokenPayload = Depends(auth_service.get_access_token_payload),
    ) -> LinkSchemaOut:
        is_admin = credentials.role == UserRole.ADMIN.value
        filters = LinkSchemaFilter(user_id=None if is_admin else credentials.user_id)
        return await link_service.retrieve_with_schema(session, link_id, filters)

    @staticmethod
    @router.post("/", status_code=status.HTTP_201_CREATED)
    async def create(
        session: AsyncSessionDep,
        obj: LinkSchemaIn,
        credentials: AccessTokenPayload = Depends(auth_service.get_access_token_payload),
    ) -> LinkSchemaOut:
        link = await link_service.create(session, credentials.user_id, obj)
        return link_service.to_schema(link)

    @staticmethod
    @router.patch("/{link_id}", status_code=status.HTTP_200_OK)
    async def update(
        session: AsyncSessionDep,
        link_id: int,
        obj: LinkSchemaUpdate,
        credentials: AccessTokenPayload = Depends(auth_service.get_access_token_payload),
    ) -> LinkSchemaOut:
        link = await link_service.update(session, link_id, credentials.user_id, obj)
        return link_service.to_schema(link)

    @staticmethod
    @router.delete("/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete(
        session: AsyncSessionDep,
        link_id: int,
        credentials: AccessTokenPayload = Depends(auth_service.get_access_token_payload),
    ) -> None:
        await link_service.delete(session, link_id, credentials.user_id)

    @staticmethod
    @router.post("/{link_id}/schema/accept", status_code=status.HTTP_204_NO_CONTENT)
    async def accept_schema(
        session: AsyncSessionDep,
        link_id: int,
        credentials: AccessTokenPayload = Depends(auth_service.get_access_token_payload),
    ) -> None:
        """Принимает изменения схемы: текущий different становится новым baseline."""
        await link_service.accept_schema(session, link_id, credentials.user_id)

    @staticmethod
    @router.get("/{link_id}/schema/{version}", status_code=status.HTTP_200_OK)
    async def get_schema_version(
        session: AsyncSessionDep,
        link_id: int,
        version: str,
        credentials: AccessTokenPayload = Depends(auth_service.get_access_token_payload),
    ) -> dict:
        """Получает конкретную версию schema.json из бакета link-schemas."""
        return await link_service.get_schema_version(
            session, link_id, credentials.user_id, version
        )


link_resolver = LinkResolver()
```

- [ ] **Step 2: Запустить все тесты**

```bash
cd backend
pytest tests/ -v
```

Expected: все тесты — PASS.

- [ ] **Step 3: Проверить импорт модуля (нет NameError)**

```bash
cd backend
python -c "from modules.link.resolver import link_resolver; print('OK')"
```

Expected: `OK` без ошибок.

- [ ] **Step 4: Commit**

```bash
git add backend/src/modules/link/resolver.py
git commit -m "refactor: LinkResolver to thin layer, add accept_schema endpoint, fix imports"
```

---

### Task 8: Финальная проверка (smoke test + интеграция)

**Files:** нет новых файлов

- [ ] **Step 1: Проверить все импорты link-модуля без ошибок**

```bash
cd backend
python -c "
from modules.link.strategies.check import check_strategy
from modules.link.strategies.schema import schema_strategy
from modules.link.service import link_service
from modules.link.resolver import link_resolver
from modules.link.tasks import LinkCheckTask
print('All imports OK')
"
```

Expected: `All imports OK` — нет TypeError, NameError, ImportError.

- [ ] **Step 2: Запустить полный набор тестов**

```bash
cd backend
pytest tests/ -v
```

Expected: все тесты — PASS, нет ошибок.

- [ ] **Step 3: Запустить бэкенд и проверить endpoints**

```bash
cd backend
uvicorn src.main:app --reload
```

В отдельном терминале:
```bash
# Проверить что /link/ отвечает
curl -s http://localhost:8000/link/ -H "Authorization: Bearer <token>" | python -m json.tool

# Проверить что /link/:id включает schema-поля (null если S3 пуст)
curl -s http://localhost:8000/link/1 -H "Authorization: Bearer <token>" | python -m json.tool
```

Expected: ответы с полями `schema`, `different`, `tag`, `attrs`, `change_percentage` (могут быть `null` если нет данных в S3).

- [ ] **Step 4: Проверить новый endpoint accept**

```bash
curl -s -X POST http://localhost:8000/link/1/schema/accept \
  -H "Authorization: Bearer <token>" \
  -w "\nHTTP %{http_code}"
```

Expected: `HTTP 204` (если schema есть в S3) или `HTTP 404` с `"Schema not found"` (если нет).

- [ ] **Step 5: Final commit**

```bash
git add -A
git commit -m "feat: link module refactor complete — schema diff with HTML normalization"
```

---

## Итог: что изменилось

| Баг/проблема | Решение |
|---|---|
| `LinkCheckStrategy()` без аргументов → crash | `CheckStrategy` — stateless, нет `__init__` |
| `get_snapshot()` без `await` | Вызов теперь с `await` в `_update_schema` |
| S3-ключи `save_check` vs `get_checks` не совпадают | Единый ключ `{user_id}/{link_id}.json` |
| `LinkModel` не импортирован в resolver | Resolver больше не использует ORM напрямую |
| Опечатка `stategies` | Файлы и классы переименованы |
| Бизнес-логика в resolver | Перенесена в service |
| God-class `LinkCheckStrategy` | Разделена на `CheckStrategy` + `SchemaStrategy` |
| God-class `LinkCheckTask` | Тонкий оркестратор, логика в service |
| Нет сравнения HTML | `SchemaStrategy.normalize_html` + `compute_change_percentage` |
| Нет поля `different` на фронт | `GET /link/:id` возвращает `schema` + `different` |
| Нет принятия изменений | `POST /link/:id/schema/accept` |
