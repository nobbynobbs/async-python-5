import asyncio
import json
import logging
from typing import List

from minechat.connection import connect
from minechat.exceptions import InvalidToken, UnknownError
import minechat.lib.gui as gui
from minechat.lib.gui import SendingConnectionStateChanged, ReadConnectionStateChanged

async def send_messages(
        address: str,
        access_token: str,
        state_queue: asyncio.Queue,
        input_queue: asyncio.Queue,
        watchdog_queue: asyncio.Queue,
):
    """send message to minechat"""
    async with connect(address, state_queue, SendingConnectionStateChanged, 1) as (reader, writer):
        account_info = await authenticate(access_token, reader, writer, watchdog_queue)

        event = gui.NicknameReceived(account_info["nickname"])
        await state_queue.put(event)

        while True:
            msg = await input_queue.get()
            logging.debug(f"Пользователь написал: {msg}")
            # message doesn't appear in the chat if only one `\n` used
            await _send(writer, _sanitize(msg, eol="\n\n"))
            await watchdog_queue.put("Message sent")


async def authenticate(token, reader, writer, watchdog_queue):
    """authenticate user by token"""
    await _read(reader)  # log auth greetings
    await watchdog_queue.put("Prompt before authentication")
    await _send(writer, "{}\n".format(token))
    response = await _read(reader)
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
    """establish connection and run reader"""
    async with connect(address, state_queue, ReadConnectionStateChanged, timeout) as (r, _):
        await _read_forever(r, message_queues, watchdog_queue)


async def _read_forever(
        reader: asyncio.StreamReader,
        queues: List[asyncio.Queue],
        watchdog_queue: asyncio.Queue,
):
    """read messages from stream reader and pass them into queues"""
    while True:
        raw_bytes = await reader.readline()
        msg = raw_bytes.decode("utf-8").strip()
        for queue in queues:
            await queue.put(msg)
        await watchdog_queue.put("New message in chat")


async def _read(reader):
    """helper for reading from stream"""
    raw_data = await reader.readline()
    decoded_data = raw_data.decode("utf-8").strip()
    logging.debug(decoded_data)
    return decoded_data


async def _send(writer, data: bytes or str):
    """helper for writing into stream"""
    if isinstance(data, str):
        data = data.encode("utf-8")
    writer.write(data)
    await writer.drain()


def _sanitize(message, eol="\n"):
    """helper function.
    truncate space symbols at the beginning
    and at the end of string,
    then replace new lines inside the string
    and at last append new line at the end of string
    """
    return "{}{}".format(message.strip().replace("\n", " "), eol)