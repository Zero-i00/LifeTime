import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Optional, Sequence

import aiohttp
from aiohttp import ClientConnectorError, ClientSSLError, ServerTimeoutError
from fastapi import status, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import IS_DEBUG, settings
from database.models import LinkModel, ProjectModel
from lib.s3 import s3_client
from modules.link.schema import LinkSchemaOut, LinkSchemaIn, LinkSchemaUpdate, LinkSchemaFilter
from modules.link.strategies.check import CheckStrategy
from modules.link.strategies.schema import SchemaStrategy

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


class LinkService:
    def __init__(self):
        self.not_found_exception = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found",
        )

    async def list(
        self, session: AsyncSession, filters: LinkSchemaFilter
    ) -> Sequence[LinkModel]:
        query = select(LinkModel)
        if filters.url is not None:
            query = query.where(LinkModel.url.ilike(f"%{filters.url}%"))
        if filters.project_id is not None:
            query = query.where(LinkModel.project_id == filters.project_id)
        if filters.user_id is not None:
            query = query.join(LinkModel.project).where(
                ProjectModel.user_id == filters.user_id
            )

        result = await session.execute(query)
        return result.scalars().all()

    async def retrieve(
        self, session: AsyncSession, link_id: int, filters: LinkSchemaFilter
    ) -> LinkModel:
        link = await session.get(LinkModel, link_id)
        if link is None:
            raise self.not_found_exception
        if filters.user_id is not None and link.project.user_id != filters.user_id:
            raise self.not_found_exception
        return link

    async def retrieve_with_schema(
        self, session: AsyncSession, link_id: int, filters: LinkSchemaFilter
    ) -> LinkSchemaOut:
        """Возвращает ссылку вместе с данными schema.json из S3."""
        link = await self.retrieve(session, link_id, filters)
        schema_data = await SchemaStrategy.get_snapshot(link.project.user_id, link_id)
        return self.to_schema(link, schema_data)

    async def create(
        self, session: AsyncSession, user_id: int, obj: LinkSchemaIn
    ) -> LinkModel:
        project = await session.get(ProjectModel, obj.project_id)
        if project is None or project.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        link = LinkModel(url=obj.url, project_id=obj.project_id)
        session.add(link)
        await session.commit()
        await session.refresh(link)
        return link

    async def update(
        self,
        session: AsyncSession,
        link_id: int,
        user_id: int,
        obj: LinkSchemaUpdate,
    ) -> LinkModel:
        link = await session.get(LinkModel, link_id)
        if link is None or link.project.user_id != user_id:
            raise self.not_found_exception

        if obj.url is not None:
            link.url = obj.url

        await session.commit()
        await session.refresh(link)
        return link

    async def delete(
        self, session: AsyncSession, link_id: int, user_id: int
    ) -> None:
        link = await session.get(LinkModel, link_id)
        if link is None or link.project.user_id != user_id:
            raise self.not_found_exception

        await session.delete(link)
        await session.commit()

    async def accept_schema(
        self, session: AsyncSession, link_id: int, user_id: int
    ) -> None:
        """Принимает изменения: текущий different становится новым baseline."""
        link = await session.get(LinkModel, link_id)
        if link is None or link.project.user_id != user_id:
            raise self.not_found_exception

        snapshot = await SchemaStrategy.get_snapshot(user_id, link_id)
        if snapshot is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Schema not found",
            )

        new_baseline = snapshot["different"]
        tag, attrs = SchemaStrategy.extract_root_info(new_baseline)

        await SchemaStrategy.save_snapshot(
            user_id,
            link_id,
            {
                "schema": new_baseline,
                "different": new_baseline,
                "tag": tag,
                "attrs": attrs,
                "change_percentage": 0.0,
            },
        )

    async def get_schema_version(
        self,
        session: AsyncSession,
        link_id: int,
        user_id: int,
        version: str,
    ) -> dict:
        """Получает версионированную схему из бакета link-schemas."""
        link = await session.get(LinkModel, link_id)
        if link is None or link.project.user_id != user_id:
            raise self.not_found_exception

        key = f"{user_id}/{link_id}/schemas/schema_{version}.json"
        data = await s3_client.get_object("link-schemas", key)

        if data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Schema version {version} not found",
            )

        try:
            return json.loads(data)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid JSON format in schema file",
            )

    async def check_link(
        self,
        link: LinkModel,
        http_session: aiohttp.ClientSession,
        timeout: int,
    ) -> None:
        """Выполняет health-check ссылки: HTTP запрос + запись в S3."""
        url = link.url
        user_id = link.project.user_id
        link_id = link.id
        is_https = url.startswith("https://")
        loop = asyncio.get_running_loop()
        start = loop.time()

        def elapsed() -> int:
            return int((loop.time() - start) * 1000)

        html: Optional[str] = None
        check_data: dict

        try:
            async with http_session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=timeout),
                allow_redirects=True,
                ssl=True,
            ) as resp:
                raw = await resp.read()
                content_length = len(raw)
                is_up = 200 <= resp.status < 400
                check_data = {
                    "status_code": resp.status,
                    "response_time_ms": elapsed(),
                    "is_up": is_up,
                    "checked_at": _now(),
                    "ssl_valid": True if is_https else None,
                    "content_length": content_length,
                    "error_message": None,
                }
                if is_up:
                    html = raw.decode("utf-8", errors="replace")
        except ClientSSLError as e:
            check_data = _error_result(elapsed(), ssl_valid=False, error=e)
        except (ClientConnectorError, ServerTimeoutError, asyncio.TimeoutError) as e:
            check_data = _error_result(elapsed(), ssl_valid=None, error=e)
        except Exception as e:
            check_data = _error_result(elapsed(), ssl_valid=None, error=e)

        if not IS_DEBUG:
            await CheckStrategy.save_check(user_id, link_id, check_data)

        if html is not None:
            await self._update_schema(user_id, link_id, html)

    async def _update_schema(
        self, user_id: int, link_id: int, html: str
    ) -> None:
        """Нормализует HTML и обновляет schema.json в S3."""
        try:
            normalized = SchemaStrategy.normalize_html(html)
            existing = await SchemaStrategy.get_snapshot(user_id, link_id)
            tag, attrs = SchemaStrategy.extract_root_info(normalized)

            if existing is None:
                await SchemaStrategy.save_snapshot(
                    user_id,
                    link_id,
                    {
                        "schema": normalized,
                        "different": normalized,
                        "tag": tag,
                        "attrs": attrs,
                        "change_percentage": 0.0,
                    },
                )
                return

            baseline = existing["schema"]
            percentage = SchemaStrategy.compute_change_percentage(baseline, normalized)

            await SchemaStrategy.save_snapshot(
                user_id,
                link_id,
                {
                    "schema": baseline,
                    "different": normalized,
                    "tag": tag,
                    "attrs": attrs,
                    "change_percentage": percentage,
                },
            )
        except Exception as exc:
            logger.warning(
                "Failed to update schema for link %s (user %s): %s",
                link_id,
                user_id,
                exc,
            )

    @staticmethod
    def to_schema(
        obj: LinkModel, schema_data: Optional[dict] = None
    ) -> LinkSchemaOut:
        return LinkSchemaOut(
            id=obj.id,
            url=obj.url,
            project_id=obj.project_id,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            schema=schema_data.get("schema") if schema_data else None,
            different=schema_data.get("different") if schema_data else None,
            tag=schema_data.get("tag") if schema_data else None,
            attrs=schema_data.get("attrs") if schema_data else None,
            change_percentage=schema_data.get("change_percentage") if schema_data else None,
        )


link_service = LinkService()
