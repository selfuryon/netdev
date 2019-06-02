"""
SSH Connection Module
"""
import asyncio

import asyncssh

from netdev.connections.io_connection import IOConnection
from netdev.constants import TERM_LEN, TERM_TYPE, TERM_WID, MAX_BUFFER
from netdev.exceptions import DisconnectError, TimeoutError
from netdev.logger import logger


class SSHConnection(IOConnection):
    """ SSH Connection Class """

    def __init__(self, host="", port=22, *, tunnel=None, loop=None, **kwargs):
        if host:
            self._host = host
        else:
            raise ValueError("Host must be set")

        self._port = port or 22
        self._loop = loop or asyncio.get_event_loop
        self._tunnel = tunnel
        self._conn_dict = kwargs
        self._conn = None
        self._stdin = None
        self._stdout = None
        self._stderr = None

    async def connect(self):
        """ Etablish the SSH connection """
        self._logger.info(
            "Host %s: Establishing SSH connection on port %s", self._host, self._port
        )
        try:
            self._conn = await asyncssh.connect(
                self._host,
                self._port,
                loop=self._loop,
                tunnel=self._tunnel,
                **self._conn_dict,
            )
        except asyncssh.DisconnectError as error:
            raise DisconnectError(self._host, error.code, error.reason)

        await self._start_session()

    async def _start_session(self):
        """ Start interactive-session (shell) """
        self._logger.info(
            "Host %s: Starting Interacive session term_type=%s, term_width=%s, term_length=%s",
            self._host,
            TERM_TYPE,
            TERM_WID,
            TERM_LEN,
        )
        self._stdin, self._stdout, self._stderr = await self._conn.open_session(
            term_type=TERM_TYPE, term_size=(TERM_WID, TERM_LEN)
        )

    async def disconnect(self):
        """ Gracefully close the SSH connection """
        self._logger.info("Host %s: Disconnecting", self._host)
        self._conn.close()
        await self._conn.wait_closed()

    def send(self, cmd):
        """ Send command to the channel"""
        self._stdin.write(cmd)

    async def read(self):
        """ Read buffer from the channel """
        return await self._stdout.read(MAX_BUFFER)

    @property
    def _logger(self):
        return logger.getChild("SSHConnection")

    @property
    def host(self):
        """ Return the host address """
        return self._host
