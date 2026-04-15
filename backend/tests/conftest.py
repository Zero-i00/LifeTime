"""
Root conftest — patches config.settings before any app module is imported,
so tests can run without real environment variables.
"""
import sys
from unittest.mock import MagicMock, patch

# Stub out the settings module before anything imports it
mock_settings = MagicMock()
mock_settings.s3.access_key = "test-key"
mock_settings.s3.secret_key = "test-secret"
mock_settings.s3.endpoint_url = "http://localhost:9000"

# Patch at the module level so downstream imports (lib.s3, etc.) get the mock
sys.modules.setdefault("config", MagicMock(settings=mock_settings))

# Also patch the specific attribute used by lib.s3
import config  # noqa: E402 — must come after sys.modules manipulation
config.settings = mock_settings
