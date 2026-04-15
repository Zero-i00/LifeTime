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
