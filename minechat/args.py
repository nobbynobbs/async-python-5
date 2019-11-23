import argparse
import os

DEFAULT_READER = "minechat.dvmn.org:5000"
DEFAULT_WRITER = "minechat.dvmn.org:5050"
DEFAULT_LOGGING_LEVEL = "INFO"
DEFAULT_HISTORY_PATH = "history.txt"


def process_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--reader", "-r",
        type=str,
        default=os.getenv("MINECHAT_READER", DEFAULT_READER),
        help="minechat messages source address"
    )

    parser.add_argument(
        "--writer", "-w",
        type=str,
        default=os.getenv("MINECHAT_WRITER", DEFAULT_WRITER),
        help="minechat messages receiver address"
    )

    parser.add_argument(
        "--token",
        "-t",
        type=str,
        help="Authorization token",
        required=False,
        default=os.getenv("MINECHAT_TOKEN", None)
    )

    parser.add_argument(
        "--level",
        "-l",
        choices=("DEBUG", "INFO", "WARNING", "ERROR",),
        type=str,
        help="logging level",
        required=False,
        default=os.getenv("MINECHAT_LOGGING_LEVEL", DEFAULT_LOGGING_LEVEL)
    )

    parser.add_argument(
        "--history",
        type=str,
        help="path to messages history",
        default=os.getenv("MINECHAT_HISTORY_PATH", DEFAULT_HISTORY_PATH),
        required=False,

    )

    return parser.parse_args()
