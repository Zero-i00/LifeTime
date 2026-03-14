import asyncio

asyncio.set_event_loop(asyncio.new_event_loop())

from arq.worker import run_worker
from worker import WorkerSettings

run_worker(WorkerSettings)
