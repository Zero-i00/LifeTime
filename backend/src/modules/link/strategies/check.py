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
