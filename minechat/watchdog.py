import asyncio
import logging

import async_timeout

import minechat.clients  as clients
from minechat.helpers import create_handy_nursery, reconnect

logger = logging.getLogger(__name__)


async def watch_for_connection(
        events_queue: asyncio.Queue,
        timeout=1,
):
    while True:
        try:
            async with async_timeout.timeout(timeout) as cm:
                event = await events_queue.get()
        except asyncio.TimeoutError:
            if cm.expired:
                logger.info(f"{timeout}s timeout is elapsed")
                raise ConnectionError
        else:
            logger.info(f"{event}")


@reconnect()
async def handle_connection(
        reader_address: str,
        writer_address: str,
        access_token: str,
        messages_queue: asyncio.Queue,
        input_queue: asyncio.Queue,
        history_queue: asyncio.Queue,
        watchdog_queue: asyncio.Queue,
        state_queue: asyncio.Queue,
):
    async with create_handy_nursery() as nursery:
        nursery.start_soon(watch_for_connection(
            events_queue=watchdog_queue
        ))
        nursery.start_soon(clients.read_messages(
            address=reader_address,
            state_queue=state_queue,
            message_queues=[messages_queue, history_queue],
            watchdog_queue=watchdog_queue,
        ))
        nursery.start_soon(clients.send_messages(
            address=writer_address,
            access_token=access_token,
            state_queue=state_queue,
            input_queue=input_queue,
            watchdog_queue=watchdog_queue,
        ))


