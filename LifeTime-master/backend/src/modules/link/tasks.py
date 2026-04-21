import asyncio
import logging
from typing import Any

import aiohttp
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from config import settings
from database.models.link import LinkModel
from database.session import session_factory
from modules.link.service import link_service

logger = logging.getLogger(__name__)


class LinkCheckTask:
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
            async def check_and_log(link: LinkModel) -> None:
                async with semaphore:
                    await link_service.check_link(link, http_session, timeout)
                    logger.info(f"Link {link.id} ({link.url}): checked")

            await asyncio.gather(*[check_and_log(link) for link in links])

        logger.info("Link health check run complete")
