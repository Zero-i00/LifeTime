import os
import pytest
from unittest.mock import AsyncMock, MagicMock

os.environ.setdefault("S3_ACCESS_KEY", "test_access_key")
os.environ.setdefault("S3_SECRET_KEY", "test_secret_key")
os.environ.setdefault("S3_ENDPOINT_URL", "http://localhost:9000")
os.environ.setdefault("S3_BUCKET_NAME", "test-bucket")


@pytest.fixture
def session():
    """Фикстура мок-сессии БД."""
    s = AsyncMock()
    s.add = MagicMock()
    s.commit = AsyncMock()
    s.refresh = AsyncMock()
    s.delete = AsyncMock()
    s.execute = AsyncMock()
    s.get = AsyncMock()
    return s