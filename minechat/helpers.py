import asyncio
import contextlib
import functools
import logging
from typing import Union, Set

import aionursery


@contextlib.asynccontextmanager
async def create_handy_nursery():
    try:
        async with aionursery.Nursery() as nursery:
            yield nursery
    except aionursery.MultiError as e:
        if len(e.exceptions) == 1:
            # suppress exception chaining
            # https://docs.python.org/3/reference/simple_stmts.html#the-raise-statement
            raise e.exceptions[0] from None
        raise


def reconnect(delay=2):
    """wraps connection handler into almost infinite loop"""
    def deco(f):
        @functools.wraps(f)
        async def wrapper(*args, **kwargs):
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


def sanitize(message: str, eol: str = "\n"):
    """helper function.
    truncate space symbols at the beginning
    and at the end of string,
    then replace new lines inside the string
    and at last append new line at the end of string
    """
    return "{}{}".format(message.strip().replace("\n", " "), eol)


async def send(writer: asyncio.StreamWriter, data: Union[bytes, str]):
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
