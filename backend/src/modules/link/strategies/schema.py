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
        raw_bytes = raw_html.encode("utf-8", errors="replace")
        if len(raw_bytes) > MAX_HTML_BYTES:
            raw_html = raw_bytes[:MAX_HTML_BYTES].decode("utf-8", errors="ignore")

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
        MAX_COMPARE = 100_000  # prevent O(n²) blocking on large pages
        ratio = difflib.SequenceMatcher(None, old[:MAX_COMPARE], new[:MAX_COMPARE]).ratio()
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
