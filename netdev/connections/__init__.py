"""
Copyright (c) 2019 Sergey Yakovlev <selfuryon@gmail.com>.

Connection init module.
"""
from netdev.connections.io_connection import IOConnection
from netdev.connections.ssh import SSHConnection
from netdev.connections.telnet import TelnetConnection


__all__ = ("IOConnection", "SSHConnection", "TelnetConnection")
