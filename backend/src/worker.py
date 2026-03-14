import asyncio

asyncio.set_event_loop(asyncio.new_event_loop())

from arq import cron
from arq.connections import RedisSettings as ArqRedisSettings

from config import settings
from modules.link.tasks import LinkCheckTask

_link_check_task = LinkCheckTask()
_minute_step = max(1, settings.worker.check_interval_seconds // 60)


class WorkerSettings:
    cron_jobs = [
        cron(
            _link_check_task.run,
            second={0},
            minute=set(range(0, 60, _minute_step)),
        )
    ]
    redis_settings = ArqRedisSettings(
        host=settings.redis.host,
        port=settings.redis.port,
    )
