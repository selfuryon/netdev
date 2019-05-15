import asyncio
import asyncssh
from netdev.exceptions import DisconnectError
from netdev.logger import logger


class SSHConnection:
    def __init__(self, connect_params_dict, timeout):
        self._conn_dict = connect_params_dict
        self._timeout = timeout
        self.host = connect_params_dict['host']

    async def __aenter__(self):
        """Async Context Manager"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async Context Manager"""
        await self.disconnect()

    async def connect(self):
        fut = asyncssh.connect(**self._conn_dict)
        try:
            self._conn = await asyncio.wait_for(fut, self._timeout)
        except asyncssh.DisconnectError as e:
            raise DisconnectError(self.host, e.code, e.reason)
        except asyncio.TimeoutError:
            raise TimeoutError(self.host)

    async def disconnect(self):
        """ Gracefully close the SSH connection """
        logger.info("Host {}: Disconnecting".format(self.host))
        logger.info("Host {}: Disconnecting".format(self.host))
        await self._cleanup()
        self._conn.close()
        await self._conn.wait_closed()

    async def _cleanup(self):
        pass
