import asyncio

import aiofiles


def restore(
        path: str,
        messages_queue: asyncio.Queue
):
    with open(path, "r", encoding="utf-8") as f:
        for msg in f:
            messages_queue.put_nowait(msg.strip())


async def save(
        path: str,
        history_queue: asyncio.Queue,
):
    async with aiofiles.open(path, "a", encoding="utf-8") as f:
        while True:
            msg = await history_queue.get()
            await f.write(msg + "\n")
