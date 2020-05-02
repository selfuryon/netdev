"""
Copyright (c) 2019 Sergey Yakovlev <selfuryon@gmail.com>.

The module contains SSH Connection class.
This class connects to devices using asyncssh.
"""
import asyncio
import logging

import asyncssh

from netdev.connections.constants import MAX_BUFFER, TERM_LEN, TERM_TYPE, TERM_WID
from netdev.connections.io_connection import IOConnection
from netdev.exceptions import DisconnectError
from netdev.logger import logger


class SSHConnection(IOConnection):
    """ SSH Connection Class """

    def __init__(
        self,
        host: str = "",
        port: int = 22,
        *,
        tunnel: asyncssh.SSHClientConnection = None,
        **kwargs,
    ) -> None:
        if host:
            self._host = host
        else:
            raise ValueError("Host must be set")

        self._port = port or 22
        self._loop = asyncio.get_event_loop()
        self._tunnel = tunnel
        self._conn_dict = kwargs
        self._conn = None
        self._stdin = None
        self._stdout = None
        self._stderr = None

    async def connect(self) -> None:
        """ Etablish the SSH connection """
        self._logger.info(
            "Host %s: Establishing SSH connection on port %s", self._host, self._port
        )
        try:
            self._conn = await asyncssh.connect(
                self._host, self._port, tunnel=self._tunnel, **self._conn_dict,
            )
        except asyncssh.DisconnectError as error:
            raise DisconnectError(self._host, error.code, error.reason)

        await self._start_session()

    async def _start_session(self) -> None:
        """ Start interactive-session (shell) """
        self._logger.info(
            "Host %s: Starting Interacive session term=%s, width=%s, length=%s",
            self.host,
            TERM_TYPE,
            TERM_WID,
            TERM_LEN,
        )
        self._stdin, self._stdout, self._stderr = await self._conn.open_session(
            term_type=TERM_TYPE, term_size=(TERM_WID, TERM_LEN)
        )

    async def disconnect(self) -> None:
        """ Gracefully close the SSH connection """
        self._logger.info("Host %s: Disconnecting", self.host)
        self._conn.close()
        await self._conn.wait_closed()

    async def send(self, cmd: str) -> None:
        """ Send command to the channel"""
        self._logger.debug("Host %s: Send to channel: %r", self.host, cmd)
        self._stdin.write(cmd)

    async def read(self) -> str:
        """ Read buffer from the channel """
        output = await self._stdout.read(MAX_BUFFER)
        self._logger.debug("Host %s: Recieved from channel: %r", self.host, output)
        return output

    @property
    def _logger(self) -> logging.Logger:
        return logger.getChild("SSHConnection")

    @property
    def host(self) -> str:
        """ Return the host address """
        return self._host
