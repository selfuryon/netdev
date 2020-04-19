"""
Copyright (c) 2020 Sergey Yakovlev <selfuryon@gmail.com>.

This module provides generic cisco device manager

"""
import logging
from enum import IntEnum
from typing import Callable

from netdev.connections import SSHConnection, TelnetConnection
from netdev.core import DeviceManager, DeviceStream, Layer, LayerManager
from netdev.logger import logger
from netdev.vendors.cisco_like import (CiscoTerminalMode, cisco_check_closure,
                                       cisco_enter_closure, cisco_exit_closure)


def initialize_cisco(
    host: str,
    username: str,
    password: str,
    conn_type: str = "ssh",
    *,
    secret: str,
    port: int = None,
    **kwargs
) -> DeviceManager:
    conn = None
    if conn_type == "ssh":
        port = port or 22
        conn = SSHConnection(host, port, **kwargs)
    elif conn_type == "telnet":
        port = port or 23
        conn = TelnetConnection(host, port, username, password, **kwargs)
    else:
        raise ValueError("Non-supported connection type")

    dstream = DeviceStream(conn, [">", "#"])
