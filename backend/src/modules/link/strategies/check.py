import json
from typing import Optional

from config import settings
from lib.s3 import S3Client


class LinkCheckStrategy:
    def __init__(self, s3_client: S3Client):
        self._s3 = s3_client
        self._bucket = settings.s3.link_statistic_bucket

    async def save_check(self, user_id: int, link_id: int, check_data: dict) -> None:
        key = f"{user_id}/{link_id}.json"
        existing = await self._s3.get_object(self._bucket, key)
        checks = json.loads(existing) if existing else []
        checks.append(check_data)
        await self._s3.put_object(self._bucket, key, json.dumps(checks).encode())

    async def get_checks(self, user_id: int, link_id: int) -> list[dict]:
        key = f"{user_id}/{link_id}.json"
        existing = await self._s3.get_object(self._bucket, key)
        if not existing:
            return []
        return json.loads(existing)
