from typing import Dict, Any


def get_dict(level: str) -> Dict[str, Any]:
    """dict config for logging module"""
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "watchdog": {
                "format": "[%(created)d] Connection is alive. %(message)s",
            }
        },
        "handlers": {
            "watchdog": {
                "formatter": "watchdog",
                "class": "logging.StreamHandler",
            },
        },
        "loggers": {
            '': {
                "level": level,
            },
            "minechat.watchdog": {
                "level": level,
                "handlers": ["watchdog"],
                "propagate": False,
            },
        },
    }
