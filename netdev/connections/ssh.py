import asyncio
import asyncssh
from netdev.exceptions import DisconnectError
from netdev.logger import logger
from .base import BaseConnection
from netdev.version import __version__


class SSHConnection(BaseConnection):
    def __init__(self,
                 host=u"",
                 username=u"",
                 password=u"",
                 port=22,
                 timeout=15,
                 loop=None,
                 known_hosts=None,
                 local_addr=None,
                 client_keys=None,
                 passphrase=None,
                 tunnel=None,
                 pattern=None,
                 agent_forwarding=False,
                 agent_path=(),
                 client_version=u"netdev-%s" % __version__,
                 family=0,
                 kex_algs=(),
                 encryption_algs=(),
                 mac_algs=(),
                 compression_algs=(),
                 signature_algs=()):
        super().__init__()
        if host:
            self.host = host
        else:
            raise ValueError("Host must be set")
        self._port = int(port)
        self._timeout = timeout
        if loop is None:
            self._loop = asyncio.get_event_loop()
        else:
            self._loop = loop

        """Convert needed connect params to a dictionary for simplicity"""
        connect_params_dict = {
            "host": self.host,
            "port": self._port,
            "username": username,
            "password": password,
            "known_hosts": known_hosts,
            "local_addr": local_addr,
            "client_keys": client_keys,
            "passphrase": passphrase,
            "tunnel": tunnel,
            "agent_forwarding": agent_forwarding,
            "loop": loop,
            "family": family,
            "agent_path": agent_path,
            "client_version": client_version,
            "kex_algs": kex_algs,
            "encryption_algs": encryption_algs,
            "mac_algs": mac_algs,
            "compression_algs": compression_algs,
            "signature_algs": signature_algs
        }

        if pattern is not None:
            self._pattern = pattern

        self._conn_dict = connect_params_dict
        self._timeout = timeout

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

    async def send(self, cmd):
        self._stdin.write()

    async def read(self):
        return self._stdout.read()

    def __check_session(self):
        if not self._stdin:
            raise RuntimeError("SSH session not started")

    async def _start_session(self):
        self._stdin, self._stdout, self._stderr = await self._conn.open_session(
            term_type="vt100", term_size=(0, 0)
        )

    async def _cleanup(self):
        pass
