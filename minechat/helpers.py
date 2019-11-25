import asyncio
import contextlib
import functools
import logging
from typing import Union, Callable, AsyncGenerator, Awaitable, Tuple, Any, Dict

import aionursery

from minechat.exceptions import InvalidAddress


@contextlib.asynccontextmanager
async def create_handy_nursery() -> AsyncGenerator[aionursery.Nursery, None]:
    try:
        async with aionursery.Nursery() as nursery:
            yield nursery
    except aionursery.MultiError as e:
        if len(e.exceptions) == 1:
            # suppress exception chaining
            # https://docs.python.org/3/reference/simple_stmts.html#the-raise-statement
            raise e.exceptions[0] from None
        raise


AsyncFunction = Callable[..., Awaitable]
AsyncFunctionDecorator = Callable[[AsyncFunction], AsyncFunction]


def reconnect(delay: float = 2) -> AsyncFunctionDecorator:
    """wraps connection handler into almost infinite loop"""
    def deco(f: AsyncFunction) -> AsyncFunction:
        @functools.wraps(f)
        async def wrapper(*args: Tuple[Any], **kwargs: Dict[str, Any]) -> None:
            while True:
                try:
                    await f(*args, **kwargs)
                except ConnectionError:
                    logging.info(
                        f"connection error, reconnect in {delay:.2f}s"
                    )
                    await asyncio.sleep(delay)
                else:
                    return
        return wrapper
    return deco


def sanitize(message: str, eol: str = "\n") -> str:
    """helper function.
    truncate space symbols at the beginning
    and at the end of string,
    then replace new lines inside the string
    and at last append new line at the end of string
    """
    return "{}{}".format(message.strip().replace("\n", " "), eol)


async def send(writer: asyncio.StreamWriter, data: Union[bytes, str]) -> None:
    """helper for writing into stream"""
    if isinstance(data, str):
        data = data.encode("utf-8")
    writer.write(data)
    await writer.drain()


async def read(reader: asyncio.StreamReader) -> str:
    """helper for reading from stream"""
    raw_data = await reader.readline()
    decoded_data = raw_data.decode("utf-8").strip()
    logging.debug(decoded_data)
    return decoded_data


def is_bot(message: str) -> bool:
    bot_names = {"Vlad", "Eva"}
    name, _ = message.split(":", 2)
    return name in bot_names


def split_address(address: str) -> Tuple[str, int]:
    try:
        host, maybe_port = address.split(":", 2)
        port = int(maybe_port)
    except ValueError:
        raise InvalidAddress(
            "Некорректный адрес сервера",
            "Проверьте что адрес серверов указан в формате host:port"
        )
    else:
        return host, port
