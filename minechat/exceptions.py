class MinechatError(Exception):
    """base exception"""


class UnknownError(Exception):
    """raised in case of unexpected errors"""


class InvalidToken(MinechatError):
    """raised if authentication failed"""
