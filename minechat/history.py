import asyncio

import aiofiles


async def restore(path: str, messages_queue: asyncio.Queue):
    """restore messages history from file"""
    try:
        async with aiofiles.open(path, "r", encoding="utf-8") as f:
            async for msg in f:
                await messages_queue.put(msg.strip())
    except FileNotFoundError:
        pass # it's ok


async def save(path: str, history_queue: asyncio.Queue):
    """dump messages history into file"""
    async with aiofiles.open(path, "a", encoding="utf-8") as f:
        while True:
            msg = await history_queue.get()
            await f.write(msg + "\n")
