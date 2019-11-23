import asyncio
import logging
import socket

import aionursery
import async_timeout

import minechat.clients as clients
from minechat.helpers import reconnect, create_handy_nursery

logger = logging.getLogger(__name__)


async def watch_for_connection(events_queue: asyncio.Queue, timeout=1):
    """check if messages received quite often"""
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
    """just starts coroutines and handle ConnectionExceptions"""
    try:
        async with create_handy_nursery() as nursery:
            nursery.start_soon(watch_for_connection(
                events_queue=watchdog_queue,
                timeout=2,
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
    except socket.gaierror:
        raise ConnectionError
    except aionursery.MultiError as ex:
        if any(isinstance(e, socket.gaierror) for e in ex.exceptions):
            raise ConnectionError
        elif any(isinstance(e, ConnectionError) for e in ex.exceptions):
            raise ConnectionError
        else:
            raise
