import asyncio
import json
import logging
from typing import List

from minechat.connection import connect
from minechat.exceptions import InvalidToken, UnknownError
import minechat.lib.gui as gui
import minechat.helpers as helpers


async def send_messages(
        address: str,
        access_token: str,
        state_queue: asyncio.Queue,
        input_queue: asyncio.Queue,
        watchdog_queue: asyncio.Queue,
):
    """send message to minechat"""
    async with connect(
            address=address,
            state_queue=state_queue,
            state_cls=gui.SendingConnectionStateChanged,
            timeout=1
    ) as (reader, writer):
        account_info = await authenticate(
            access_token, reader, writer, watchdog_queue
        )

        event = gui.NicknameReceived(account_info["nickname"])
        await state_queue.put(event)

        async with helpers.create_handy_nursery() as nursery:
            nursery.start_soon(
                _send_user_messages(writer, input_queue, watchdog_queue)
            )
            nursery.start_soon(_send_healthcheck_messages(writer, 1))
            nursery.start_soon(
                _read_healthcheck_messages(reader, watchdog_queue)
            )


async def _send_user_messages(
        writer: asyncio.StreamWriter,
        input_queue: asyncio.Queue,
        watchdog_queue: asyncio.Queue,
):
    """read messages from queue and send them to server"""
    while True:
        msg = await input_queue.get()
        logging.debug(f"Пользователь написал: {msg}")
        # message doesn't appear in the chat if only one `\n` used
        await helpers.send(writer, helpers.sanitize(msg, eol="\n\n"))
        await watchdog_queue.put("Message sent")


async def _send_healthcheck_messages(
        writer: asyncio.StreamWriter, interval: float = 0.5
):
    """send pings to server"""
    while True:
        writer.write(b"\n")
        await writer.drain()
        await asyncio.sleep(interval)


async def _read_healthcheck_messages(
        reader: asyncio.StreamReader, watchdog_queue: asyncio.Queue
):
    """read server responses to pings"""
    while True:
        _ = await reader.readline()
        await watchdog_queue.put("Healthcheck message")


async def authenticate(token, reader, writer, watchdog_queue):
    """authenticate user by token"""
    await helpers.read(reader)  # read auth greeting
    await watchdog_queue.put("Prompt before authentication")
    await helpers.send(writer, "{}\n".format(token))
    response = await helpers.read(reader)
    try:
        account_info = json.loads(response)
    except json.JSONDecodeError:
        logging.error("invalid json in authentication response")
        raise UnknownError
    else:
        if account_info is None:
            raise InvalidToken
        await watchdog_queue.put("Authenticated")
        return account_info


async def read_messages(
        address: str,
        state_queue: asyncio.Queue,
        message_queues: List[asyncio.Queue],
        watchdog_queue: asyncio.Queue,
        timeout: float = 1
):
    """establish connection and then
    read messages from stream reader and pass them into queues
    """
    async with connect(
            address=address,
            state_queue=state_queue,
            state_cls=gui.ReadConnectionStateChanged,
            timeout=timeout
    ) as (reader, _):
        while True:
            raw_bytes = await reader.readline()
            msg = raw_bytes.decode("utf-8").strip()
            await watchdog_queue.put("New message in chat")
            for queue in message_queues:
                await queue.put(msg)
