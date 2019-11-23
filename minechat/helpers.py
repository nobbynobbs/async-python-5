import asyncio
import contextlib
import functools
import logging

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
