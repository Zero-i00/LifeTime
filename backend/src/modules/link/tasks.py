import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Optional

import aiohttp
from aiohttp import ClientConnectorError, ClientSSLError, ServerTimeoutError
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from config import IS_DEBUG, settings
from database.models.link import LinkModel
from database.session import session_factory
from lib.s3 import s3_client
from modules.link.strategies.check import LinkCheckStrategy

logger = logging.getLogger(__name__)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _error_result(elapsed_ms: int, ssl_valid: Optional[bool], error: Exception) -> dict:
    return {
        "status_code": None,
        "response_time_ms": elapsed_ms,
        "is_up": False,
        "checked_at": _now(),
        "ssl_valid": ssl_valid,
        "content_length": None,
        "error_message": str(error),
    }


class LinkCheckTask:
    def __init__(self):
        self._strategy = LinkCheckStrategy(s3_client)

    async def _check_single_link(
        self,
        http_session: aiohttp.ClientSession,
        url: str,
        timeout: int,
    ) -> dict:
        is_https = url.startswith("https://")
        loop = asyncio.get_running_loop()
        start = loop.time()

        def elapsed() -> int:
            return int((loop.time() - start) * 1000)

        try:
            async with http_session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=timeout),
                allow_redirects=True,
                ssl=True,
            ) as resp:
                content_length = resp.content_length
                if content_length is None:
                    content_length = len(await resp.read())
                return {
                    "status_code": resp.status,
                    "response_time_ms": elapsed(),
                    "is_up": 200 <= resp.status < 400,
                    "checked_at": _now(),
                    "ssl_valid": True if is_https else None,
                    "content_length": content_length,
                    "error_message": None,
                }
        except ClientSSLError as e:
            return _error_result(elapsed(), ssl_valid=False, error=e)
        except (ClientConnectorError, ServerTimeoutError, asyncio.TimeoutError) as e:
            return _error_result(elapsed(), ssl_valid=None, error=e)
        except Exception as e:
            return _error_result(elapsed(), ssl_valid=None, error=e)

    async def run(self, ctx: dict[str, Any]) -> None:
        logger.info("Starting link health check run")

        semaphore = asyncio.Semaphore(settings.worker.max_concurrent_checks)
        timeout = settings.worker.request_timeout_seconds

        async with session_factory() as session:
            result = await session.execute(
                select(LinkModel).options(joinedload(LinkModel.project))
            )
            links = result.scalars().all()

        if not links:
            logger.info("No links to check")
            return

        logger.info(f"Checking {len(links)} links")

        async with aiohttp.ClientSession() as http_session:
            async def check_and_save(link: LinkModel) -> None:
                async with semaphore:
                    check_data = await self._check_single_link(http_session, link.url, timeout)
                    if not IS_DEBUG:
                        await self._strategy.save_check(link.project.user_id, link.id, check_data)
                    status = "up" if check_data["is_up"] else "down"
                    logger.info(f"Link {link.id} ({link.url}): {status}")

            await asyncio.gather(*[check_and_save(link) for link in links])

        logger.info("Link health check run complete")
