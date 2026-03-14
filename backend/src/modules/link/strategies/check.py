import json

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
