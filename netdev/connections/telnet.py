"""
Copyright (c) 2019 Sergey Yakovlev <selfuryon@gmail.com>.

The module contains Telnet Connection class.
This class connects to devices using asyncio protocol.
"""
import asyncio

from netdev.connections.io_connection import IOConnection
from netdev.constants import MAX_BUFFER
from netdev.exceptions import DisconnectError, TimeoutError
from netdev.logger import logger


class TelnetConnection(IOConnection):
    """ Telnet Connection Class """

    def __init__(
        self, host=u"", port=23, *, username=u"", password=u"", family=0, flags=0
    ):
        if host:
            self._host = host
        else:
            raise ValueError("Host must be set")
        self._port = port or 23
        self._username = username
        self._password = password
        self._loop = asyncio.get_event_loop()
        self._conn_dict = {"family": family, "flags": flags}
        self._stdout = None
        self._stdin = None

    async def connect(self):
        """ Establish the Telnet Connection """
        self._logger.info(
            "Host %s: Establishing Telnet Connection on port %s", self._host, self._port
        )
        try:
            self._stdout, self._stdin = await asyncio.open_connection(
                self._host, self._port, **self._conn_dict
            )
        except Exception as error:
            raise DisconnectError(self._host, None, str(error))

    async def disconnect(self):
        """ Gracefully close the Telnet Connection """
        self._logger.info("Host %s: Disconnecting", self._host)
        self._stdin.close()
        await self._stdin.wait_closed()

    def send(self, cmd):
        """ Send command to the channel"""
        self._stdin.write(cmd.encode())

    async def read(self):
        """ Read buffer from the channel """
        output = await self._stdout.read(MAX_BUFFER)
        return output.decode(errors="ignore")

    @property
    def _logger(self):
        return logger.getChild("TelnetConnection")

    @property
    def host(self):
        """ Return the host address """
        return self._host
