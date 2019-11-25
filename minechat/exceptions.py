class MinechatError(Exception):
    """base exception"""
    def __init__(self, title: str, message: str) -> None:
        self.title = title
        self.message = message
        super().__init__(title, message)


class UnknownError(MinechatError):
    """raised in case of unexpected errors"""


class InvalidToken(MinechatError):
    """raised if authentication failed"""


class InvalidAddress(MinechatError):
    """raised if server address passed in wrong format"""


class PermissionError(MinechatError):
    """raised if server address passed in wrong format"""
