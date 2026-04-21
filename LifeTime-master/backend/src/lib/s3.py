from contextlib import asynccontextmanager
from typing import Optional

import aiobotocore.session

from config import settings


class S3Client:
    def __init__(self, access_key: str, secret_key: str, endpoint_url: str):
        self._access_key = access_key
        self._secret_key = secret_key
        self._endpoint_url = endpoint_url
        self._session = aiobotocore.session.get_session()

    @asynccontextmanager
    async def _get_client(self):
        async with self._session.create_client(
            "s3",
            endpoint_url=self._endpoint_url,
            aws_access_key_id=self._access_key,
            aws_secret_access_key=self._secret_key,
        ) as client:
            yield client

    async def get_object(self, bucket: str, key: str) -> Optional[bytes]:
        async with self._get_client() as client:
            try:
                response = await client.get_object(Bucket=bucket, Key=key)
                async with response["Body"] as stream:
                    return await stream.read()
            except Exception:
                return None

    async def put_object(self, bucket: str, key: str, data: bytes) -> None:
        async with self._get_client() as client:
            await client.put_object(Bucket=bucket, Key=key, Body=data)

    async def delete_object(self, bucket: str, key: str) -> None:
        async with self._get_client() as client:
            await client.delete_object(Bucket=bucket, Key=key)


s3_client = S3Client(
    access_key=settings.s3.access_key,
    secret_key=settings.s3.secret_key,
    endpoint_url=settings.s3.endpoint_url,
)
