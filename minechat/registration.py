"""
Just tkinter and sockets, not asyncio
I think it's a masterpiece, looks even uglier than that old keygen-tools.
"""


import json
import socket
import tkinter as tk
import tkinter.messagebox as messagebox

import minechat.helpers as helpers


BUFFER_SIZE = 2048


def register(
        name_field: tk.Entry,
        address_field: tk.Entry,
        token_var: tk.StringVar
) -> None:
    """register new user"""

    name = name_field.get().strip()
    address = address_field.get().strip()

    if not name or not address:
        messagebox.showinfo(
            "Ошибка", "Ник, адрес и порт сервера должны быть указаны"
        )
        return

    host, port = address.split(":")
    with socket.create_connection((host, port), timeout=2) as s:
        s.recv(BUFFER_SIZE)  # skip greeting
        s.sendall(b"\n")  # skip auth
        s.recv(BUFFER_SIZE)  # skip registration greetings
        s.sendall(helpers.sanitize(name).encode("utf-8"))  # send name
        # there is very fragile piece of code below
        # but I'm too lazy to implementing something like "readline"
        raw_bytes = s.recv(BUFFER_SIZE)
        response = raw_bytes.decode("utf-8").split("\n")
        try:
            account = json.loads(response[0])
        except json.JSONDecodeError:
            messagebox.showinfo(
                "Ошибка", "Неожиданный ответ сервера, повторите попытку позже"
            )
        else:
            token_var.set(account["account_hash"])


def copy_token(root: tk.Tk, token_var: tk.StringVar) -> None:
    """copy token value to clipboard"""
    token = token_var.get()
    root.clipboard_clear()
    root.clipboard_append(token)
    root.update()


def main() -> None:
    root = tk.Tk()
    token_var = tk.StringVar()

    root.title('Чат Майнкрафтера')

    root_frame = tk.Frame()
    root_frame.pack(fill="both", expand=True)

    address_frame = tk.Frame(root_frame)
    address_frame.pack(side="top", fill=tk.X)

    address_label = tk.Label(address_frame, text="Адрес сервера:")
    address_label.pack(side="left", fill=tk.X)

    address_field = tk.Entry(address_frame)
    address_field.insert(0,  "minechat.dvmn.org:5050")
    address_field.pack(side="left", fill=tk.X, expand=True)

    name_frame = tk.Frame(root_frame)
    name_frame.pack(side="top", fill=tk.X)

    name_label = tk.Label(name_frame, text="Никнейм:")
    name_label.pack(side="left", fill=tk.X)

    name_field = tk.Entry(name_frame)
    name_field.pack(side="left", fill=tk.X, expand=True)

    name_field.bind(
        "<Return>",
        lambda event: register(name_field, address_field, token_var)
    )

    send_button = tk.Button(
        name_frame,
        text="Отправить",
        command=lambda: register(name_field, address_field, token_var)
    )
    send_button.pack(side="left")

    token_frame = tk.Frame(root_frame)
    token_frame.pack(side="bottom", fill=tk.X)

    token_label = tk.Label(token_frame, text="Токен:")
    token_label.pack(side="left", fill=tk.X)

    token_entry = tk.Entry(
        token_frame, textvariable=token_var,
    )  # I don't know if I should use state="readonly" here
    token_entry.pack(side="left", fill=tk.X, expand=True)

    copy_button = tk.Button(token_frame)
    copy_button["text"] = "Copy to clipboard"
    copy_button["command"] = lambda: copy_token(root, token_var)
    copy_button.pack(side="left")

    tk.mainloop()
