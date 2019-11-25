import asyncio

import aiofiles

from minechat import exceptions


async def restore(path: str, messages_queue: asyncio.Queue) -> None:
    """restore messages history from file"""
    try:
        async with aiofiles.open(path, "r", encoding="utf-8") as f:
            async for msg in f:
                await messages_queue.put(msg.strip())
    except FileNotFoundError:
        pass  # it's ok


async def save(path: str, history_queue: asyncio.Queue) -> None:
    """dump messages history into file"""
    try:
        async with aiofiles.open(path, "a", encoding="utf-8") as f:
            while True:
                msg = await history_queue.get()
                await f.write(msg + "\n")
    except PermissionError as ex:
        raise exceptions.PermissionError(
            "Не могу открыть файл",
            f"Проверьте что файл {ex.filename} доступен для записи"
        )
