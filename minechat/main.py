import argparse
import asyncio
import logging
import logging.config
import tkinter.messagebox as messagebox
from typing import List

import minechat.args as args
import minechat.history as history
import minechat.lib.gui as gui
from minechat.exceptions import InvalidToken, UnknownError
from minechat.helpers import create_handy_nursery
from minechat.logger_config import DEFAULT_LOGGING
from minechat.watchdog import handle_connection


def send_greetings(greetings: List[str], messages_queue: asyncio.Queue):
    for greeting in greetings:
        messages_queue.put_nowait(greeting)


async def run_app(
        reader_address: str,
        writer_address: str,
        access_token: str,
        messages_queue: asyncio.Queue,
        input_queue: asyncio.Queue,
        history_queue: asyncio.Queue,
        history_path: str,
        watchdog_queue: asyncio.Queue,
        state_queue: asyncio.Queue,
):
    async with create_handy_nursery() as nursery:
        nursery.start_soon(handle_connection(
            reader_address=reader_address,
            writer_address=writer_address,
            access_token=access_token,
            messages_queue=messages_queue,
            input_queue=input_queue,
            history_queue=history_queue,
            watchdog_queue=watchdog_queue,
            state_queue=state_queue,
        ))
        nursery.start_soon(history.save(
            path=history_path,
            history_queue=history_queue,
        ))
        nursery.start_soon(gui.draw(
            messages_queue=messages_queue,
            sending_queue=input_queue,
            status_updates_queue=state_queue,
        ))


def main():
    logging.config.dictConfig(DEFAULT_LOGGING)

    params = args.process_args()
    # logging.basicConfig(level=getattr(logging, params.level, logging.INFO))
    # logging.debug(params)

    greetings = ["Привет обитателям чата!", "Как дела?"]

    messages_queue = asyncio.Queue()
    sending_queue = asyncio.Queue()
    status_updates_queue = asyncio.Queue()
    history_queue = asyncio.Queue()
    watchdog_queue = asyncio.Queue()

    send_greetings(greetings, messages_queue)
    history.restore(params.history, messages_queue)

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_app(
            reader_address=params.reader,
            writer_address=params.writer,
            access_token=params.token,
            messages_queue=messages_queue,
            input_queue=sending_queue,
            history_queue=history_queue,
            history_path=params.history,
            watchdog_queue=watchdog_queue,
            state_queue=status_updates_queue,
        ))
    except InvalidToken:
        messagebox.showinfo("Неверный токен", "Проверьте токен, сервер его не узнал.")
    except UnknownError:
        messagebox.showinfo("Неизвестная ошибка", "Произошла неизвестная ошибка и приложение будет закрыто.")
    except (KeyboardInterrupt, gui.TkAppClosed):
        pass


if __name__ == '__main__':
    main()
