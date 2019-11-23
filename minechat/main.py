import asyncio
import logging
import logging.config
import tkinter.messagebox as messagebox
from typing import List

import minechat.args as args
import minechat.history as history
import minechat.lib.gui as gui
from minechat import logger_config
from minechat.exceptions import InvalidToken, UnknownError
from minechat.helpers import create_handy_nursery
from minechat.watchdog import handle_connection


async def send_greetings(greetings: List[str], messages_queue: asyncio.Queue):
    """send greetings into messages queue"""
    for greeting in greetings:
        await messages_queue.put(greeting)


async def run_app(
        reader_address: str,
        writer_address: str,
        access_token: str,
        history_path: str,
        greetings: List[str],
):
    """entry point coroutine, just runs all the things"""

    messages_queue = asyncio.Queue()
    sending_queue = asyncio.Queue()
    status_updates_queue = asyncio.Queue()
    history_queue = asyncio.Queue()
    watchdog_queue = asyncio.Queue()

    async with create_handy_nursery() as nursery:
        # it's messages queue consumer, so run it first in background
        nursery.start_soon(gui.draw(
            messages_queue=messages_queue,
            sending_queue=sending_queue,
            status_updates_queue=status_updates_queue,
        ))

        # send greetings and history into messages queue
        await send_greetings(greetings, messages_queue)
        await history.restore(history_path, messages_queue)

        nursery.start_soon(history.save(
            path=history_path,
            history_queue=history_queue,
        ))
        nursery.start_soon(handle_connection(
            reader_address=reader_address,
            writer_address=writer_address,
            access_token=access_token,
            messages_queue=messages_queue,
            input_queue=sending_queue,
            history_queue=history_queue,
            watchdog_queue=watchdog_queue,
            state_queue=status_updates_queue,
        ))


def main():
    """entry point to application"""

    params = args.process_args()

    dict_config = logger_config.get_dict(params.level)
    logging.config.dictConfig(dict_config)

    # well... just hardcode it here
    greetings = ["Привет обитателям чата!", "Как дела?"]

    try:
        asyncio.run(run_app(
            reader_address=params.reader,
            writer_address=params.writer,
            access_token=params.token,
            history_path=params.history,
            greetings=greetings,
        ))
    except InvalidToken:
        messagebox.showinfo(
            "Неверный токен",
            "Проверьте токен, сервер его не узнал."
        )
    except UnknownError:
        messagebox.showinfo(
            "Неизвестная ошибка",
            "Произошла неизвестная ошибка, приложение будет закрыто."
        )
    except PermissionError as e:
        messagebox.showinfo(
            e.__class__.__name__,
            f"Невозможно получить доступ к файлу {e.filename}"
        )
    except (KeyboardInterrupt, gui.TkAppClosed):
        pass


if __name__ == '__main__':
    main()
