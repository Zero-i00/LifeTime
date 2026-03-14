import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Optional

import aiohttp
from aiohttp import ClientSSLError, ClientConnectorError, ServerTimeoutError
from arq import cron
from arq.connections import RedisSettings as ArqRedisSettings
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from config import settings, IS_DEBUG
from database.models.link import LinkModel
from database.session import session_factory
from lib.s3 import s3_client
from modules.link.strategies.check import LinkCheckStrategy

logger = logging.getLogger(__name__)


async def check_single_link(
    http_session: aiohttp.ClientSession,
    url: str,
    timeout: int,
) -> dict:
    is_https = url.startswith("https://")
    ssl_valid: Optional[bool] = None
    loop = asyncio.get_running_loop()
    start = loop.time()

    try:
        async with http_session.get(
            url,
            timeout=aiohttp.ClientTimeout(total=timeout),
            allow_redirects=True,
            ssl=True,
        ) as resp:
            elapsed_ms = int((loop.time() - start) * 1000)
            content_length = resp.content_length
            if content_length is None:
                body = await resp.read()
                content_length = len(body)
            if is_https:
                ssl_valid = True
            return {
                "status_code": resp.status,
                "response_time_ms": elapsed_ms,
                "is_up": 200 <= resp.status < 400,
                "checked_at": datetime.now(timezone.utc).isoformat(),
                "ssl_valid": ssl_valid,
                "content_length": content_length,
                "error_message": None,
            }
    except ClientSSLError as e:
        elapsed_ms = int((loop.time() - start) * 1000)
        return {
            "status_code": None,
            "response_time_ms": elapsed_ms,
            "is_up": False,
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "ssl_valid": False,
            "content_length": None,
            "error_message": f"SSL error: {e}",
        }
    except (ClientConnectorError, ServerTimeoutError, asyncio.TimeoutError) as e:
        elapsed_ms = int((loop.time() - start) * 1000)
        return {
            "status_code": None,
            "response_time_ms": elapsed_ms,
            "is_up": False,
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "ssl_valid": None,
            "content_length": None,
            "error_message": str(e),
        }
    except Exception as e:
        elapsed_ms = int((loop.time() - start) * 1000)
        return {
            "status_code": None,
            "response_time_ms": elapsed_ms,
            "is_up": False,
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "ssl_valid": None,
            "content_length": None,
            "error_message": str(e),
        }


async def check_all_links(ctx: dict[str, Any]) -> None:
    logger.info("Starting link health check run")

    strategy = LinkCheckStrategy(s3_client)
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
                check_data = await check_single_link(http_session, link.url, timeout)
                user_id = link.project.user_id
                if not IS_DEBUG:
                    await strategy.save_check(user_id, link.id, check_data)
                status = "up" if check_data["is_up"] else "down"
                logger.info(f"Link {link.id} ({link.url}): {status}")

        await asyncio.gather(*[check_and_save(link) for link in links])

    logger.info("Link health check run complete")


_minute_step = max(1, settings.worker.check_interval_seconds // 60)


class WorkerSettings:
    cron_jobs = [
        cron(
            check_all_links,
            second={0},
            minute=set(range(0, 60, _minute_step)),
        )
    ]
    redis_settings = ArqRedisSettings(
        host=settings.redis.host,
        port=settings.redis.port,
    )
