import asyncio
import contextlib

from typing import Tuple, Any, Generator, Type, TypeVar
from minechat.lib.gui import ReadConnectionStateChanged, SendingConnectionStateChanged


StateChanged = TypeVar("StateChanged", ReadConnectionStateChanged, SendingConnectionStateChanged)


@contextlib.asynccontextmanager
async def connect(
        address: str,
        state_queue: asyncio.Queue,
        state_cls: Type[StateChanged],
        timeout:float = 1
) -> Generator[Any, None, Tuple[asyncio.StreamReader, asyncio.StreamWriter]]:
    host, port = address.split(":")
    writer: asyncio.StreamWriter  # "define" variable for autocomplete purposes
    await state_queue.put(state_cls.INITIATED)
    reader, writer = await asyncio.wait_for(
        asyncio.open_connection(host, port),
        timeout
    )
    await state_queue.put(state_cls.ESTABLISHED)
    try:
        yield reader, writer
    finally:
        writer.close()
        await writer.wait_closed()
        await state_queue.put(state_cls.CLOSED)
