import aionursery
import pytest

import minechat.helpers as helpers
from minechat.exceptions import InvalidAddress


@pytest.mark.asyncio
async def test_reconnect_return():
    count = 0

    async def f():
        nonlocal count
        count += 1
        return

    f = helpers.reconnect(0)(f)
    await f()
    assert count == 1


@pytest.mark.asyncio
async def test_reconnect_connection_exceptions():
    count = 0
    want = 3

    async def f():
        nonlocal count
        count += 1
        if count < want:
            raise ConnectionError
        return

    f = helpers.reconnect(0)(f)
    await f()
    assert count == want


@pytest.mark.parametrize("address", ["host", "host:port"])
def test_split_address_must_raise(address):
    with pytest.raises(InvalidAddress):
        helpers.split_address(address)


@pytest.mark.parametrize(
    "address,host,port",
    [
        ("10.0.2.170:8000", "10.0.2.170", 8000),
        ("hostname:8080", "hostname", 8080),
    ],
    ids=["10.0.2.170:8000", "hostname:8080"]
)
def test_split_address_must_pass(address, host, port):
    got_host, got_post = helpers.split_address(address)
    assert got_host == host
    assert got_post == port


@pytest.mark.asyncio
async def test_handy_nursery_single_exception():
    async def f():
        raise ValueError

    with pytest.raises(ValueError):
        async with helpers.create_handy_nursery() as nursery:
            nursery.start_soon(f())


@pytest.mark.asyncio
async def test_handy_nursery_multiple_exception():
    async def f():
        raise ValueError

    async def g():
        raise KeyError

    with pytest.raises(aionursery.MultiError):
        async with helpers.create_handy_nursery() as nursery:
            nursery.start_soon(f())
            nursery.start_soon(g())
