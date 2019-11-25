import asyncio
import contextlib

from typing import Tuple, Type, TypeVar, AsyncGenerator

import async_timeout

from minechat import helpers
from minechat.lib import gui


StateChanged = TypeVar(
    "StateChanged",
    gui.ReadConnectionStateChanged,
    gui.SendingConnectionStateChanged
)


@contextlib.asynccontextmanager
async def connect(
        address: str,
        state_queue: asyncio.Queue,
        state_cls: Type[StateChanged],
        timeout: float = 1,
) -> AsyncGenerator[Tuple[asyncio.StreamReader, asyncio.StreamWriter], None]:
    """create connection and send statuses into queue"""

    host, port = helpers.split_address(address)
    await state_queue.put(state_cls.INITIATED)
    try:
        async with async_timeout.timeout(timeout):
            reader, writer = await asyncio.open_connection(host, port)
    except asyncio.TimeoutError:
        raise ConnectionError
    await state_queue.put(state_cls.ESTABLISHED)
    try:
        yield reader, writer
    finally:
        writer.close()
        await writer.wait_closed()
        await state_queue.put(state_cls.CLOSED)
        await state_queue.put(gui.NicknameReceived("неизвестно"))
