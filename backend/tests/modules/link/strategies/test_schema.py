import json
import pytest
from unittest.mock import AsyncMock, patch

from modules.link.strategies.schema import SchemaStrategy


# --- normalize_html тесты ---

def test_normalize_html_removes_script_tags():
    html = "<html><body><script>alert(1)</script><p>Hello</p></body></html>"
    result = SchemaStrategy.normalize_html(html)
    assert "<script>" not in result
    assert "Hello" in result


def test_normalize_html_removes_style_tags():
    html = "<html><head><style>body{color:red}</style></head><body><p>Hi</p></body></html>"
    result = SchemaStrategy.normalize_html(html)
    assert "<style>" not in result
    assert "Hi" in result


def test_normalize_html_sorts_attributes():
    html = '<html><body><div z-attr="1" a-attr="2">text</div></body></html>'
    result = SchemaStrategy.normalize_html(html)
    # z-attr должен идти после a-attr
    a_pos = result.find("a-attr")
    z_pos = result.find("z-attr")
    assert a_pos < z_pos


def test_normalize_html_removes_dynamic_attrs():
    html = '<html><body><form data-csrf-token="abc123" class="form">text</form></body></html>'
    result = SchemaStrategy.normalize_html(html)
    assert "abc123" not in result
    assert "form" in result  # class должен остаться


def test_normalize_html_returns_prettified_string():
    html = "<html><body><p>Test</p></body></html>"
    result = SchemaStrategy.normalize_html(html)
    assert isinstance(result, str)
    assert "\n" in result  # prettified содержит переносы строк


# --- extract_root_info тесты ---

def test_extract_root_info_html():
    html = '<html lang="en"><body></body></html>'
    tag, attrs = SchemaStrategy.extract_root_info(html)
    assert tag == "html"
    assert attrs.get("lang") == "en"


# --- compute_change_percentage тесты ---

def test_compute_change_percentage_identical():
    html = "<html><body><p>Hello</p></body></html>"
    result = SchemaStrategy.compute_change_percentage(html, html)
    assert result == 0.0


def test_compute_change_percentage_different():
    old = "<html><body><p>Hello</p></body></html>"
    new = "<html><body><p>World</p><section>New</section></body></html>"
    result = SchemaStrategy.compute_change_percentage(old, new)
    assert 0 < result <= 100


def test_compute_change_percentage_returns_float():
    result = SchemaStrategy.compute_change_percentage("abc", "xyz")
    assert isinstance(result, float)


# --- save_snapshot / get_snapshot тесты ---

@pytest.mark.asyncio
async def test_save_snapshot_uses_correct_key():
    mock_s3 = AsyncMock()
    mock_s3.put_object = AsyncMock()

    with patch("modules.link.strategies.schema.s3_client", mock_s3):
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
        result = await SchemaStrategy.get_snapshot(1, 42)

    assert result == data


@pytest.mark.asyncio
async def test_get_snapshot_returns_none_when_missing():
    mock_s3 = AsyncMock()
    mock_s3.get_object = AsyncMock(return_value=None)

    with patch("modules.link.strategies.schema.s3_client", mock_s3):
        result = await SchemaStrategy.get_snapshot(1, 42)

    assert result is None
