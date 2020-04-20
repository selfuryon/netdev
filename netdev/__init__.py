"""
Copyright (c) 2019 Sergey Yakovlev <selfuryon@gmail.com>.

Vendors unit module
"""

from netdev.dispatcher import create, platforms
from netdev.exceptions import CommitError, DisconnectError, TimeoutError
from netdev.logger import logger

__all__ = (
    "create",
    "platforms",
    "logger",
    "DisconnectError",
    "TimeoutError",
    "CommitError",
)
