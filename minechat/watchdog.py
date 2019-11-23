import asyncio
import logging


logger = logging.getLogger(__name__)


async def watch_for_connection(
        events_queue: asyncio.Queue
):
    while True:
        event = await events_queue.get()
        logger.info(f"{event}")
