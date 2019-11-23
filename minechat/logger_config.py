DEFAULT_LOGGING = {
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
            "level": "INFO",
        },
        "minechat.watchdog": {
            "level": "INFO",
            "handlers": ["watchdog"],
            "propagate": False,
        },
    },
}
