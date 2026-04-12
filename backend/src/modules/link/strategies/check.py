import json
from typing import Optional

from lib.s3 import S3Client

LINK_STATISTIC_BUCKET = "link-statistic-bucket-1"


class LinkCheckStrategy:
    def __init__(self, s3_client: S3Client):
        self._s3 = s3_client

    async def save_check(self, user_id: int, link_id: int, check_data: dict) -> None:
        key = f"user [{user_id}]/{link_id}.json"
        existing = await self._s3.get_object(LINK_STATISTIC_BUCKET, key)
        checks = json.loads(existing) if existing else []
        checks.append(check_data)
        await self._s3.put_object(LINK_STATISTIC_BUCKET, key, json.dumps(checks).encode())

    async def get_checks(self, user_id: int, link_id: int) -> list[dict]:
        key = f"{user_id}/{link_id}.json"
        existing = await self._s3.get_object(LINK_STATISTIC_BUCKET, key)
        return json.loads(existing) if existing else []


    # FIXME Заменить content: str на dict 
    async def save_snapshot(self, user_id: int, link_id: int, content: str) -> None:
        """
        Save page snapshot (HTML/text) as schema.json in S3.
        The key format: {user_id}/{link_id}/schema.json
        """
        key = f"{user_id}/{link_id}/schema.json"
        await self._s3.put_object(LINK_STATISTIC_BUCKET, key, content.encode())

    # FIXME Заменить content: str на dict
    async def get_snapshot(self, user_id: int, link_id: int) -> Optional[str]:
        """
        Retrieve saved snapshot from S3, or None if not found.
        """
        key = f"{user_id}/{link_id}/schema.json"
        data = await self._s3.get_object(LINK_STATISTIC_BUCKET, key)
        return data.decode() if data else None

    async def compare_with_snapshot(self, user_id: int, link_id: int, current_content: str) -> bool:
        """
        Compare current content with stored snapshot.
        - If snapshot doesn't exist, saves current and returns False.
        - If snapshot exists and differs, returns True (indicates change).
        - If snapshot exists and matches, returns False.
        """
        snapshot = await self.get_snapshot(user_id, link_id)
        if snapshot is None:
            await self.save_snapshot(user_id, link_id, current_content)
            return False
        return snapshot != current_content
    

link_check_stategies = LinkCheckStrategy()
