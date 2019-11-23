import asyncio
import logging
import logging.config
import tkinter.messagebox as messagebox
from typing import List

import minechat.args as args
import minechat.clients as clients
import minechat.history as history
import minechat.lib.gui as gui
from minechat.exceptions import InvalidToken, UnknownError
from minechat.logger_config import DEFAULT_LOGGING
from minechat.watchdog import watch_for_connection


def send_greetings(greetings: List[str], messages_queue: asyncio.Queue):
    for greeting in greetings:
        messages_queue.put_nowait(greeting)


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
        loop.run_until_complete(
            asyncio.gather(
                clients.read_messages(
                    address=params.reader,
                    state_queue=status_updates_queue,
                    message_queues=[messages_queue, history_queue],
                    watchdog_queue=watchdog_queue,
                ),
                clients.send_messages(address=params.writer, access_token=params.token,
                                      state_queue=status_updates_queue, input_queue=sending_queue,
                                      watchdog_queue=watchdog_queue),
                history.save(params.history, history_queue),
                gui.draw(messages_queue, sending_queue, status_updates_queue),
                watch_for_connection(watchdog_queue)
        ))
    except InvalidToken:
        messagebox.showinfo("Неверный токен", "Проверьте токен, сервер его не узнал.")
    except UnknownError:
        messagebox.showinfo("Неизвестная ошибка", "Произошла неизвестная ошибка и приложение будет закрыто.")
    except (KeyboardInterrupt, gui.TkAppClosed):
        pass


if __name__ == '__main__':
    main()
