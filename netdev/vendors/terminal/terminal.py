import re

from ..base import BaseDevice
from ..logger import logger


class Terminal(BaseDevice):
    """Class for working with General Terminal"""

    def __init__(self, host=u'', username=u'', password=u'', port=22, device_type=u'', known_hosts=None,
                 delimeter_list=None, local_addr=None, client_keys=None, passphrase=None, loop=None):
        """
        Initialize class for asynchronous working with network devices
        Invoke init with some special params (base_pattern and username)

        :param str host: device hostname or ip address for connection
        :param str username: username for logging to device
        :param str password: user password for logging to device
        :param int port: ssh port for connection. Default is 22
        :param str device_type: network device type
        :param known_hosts: file with known hosts. Default is None (no policy). With () it will use default file
        :param delimeter_list: list with delimeters
        :param str local_addr: local address for binding source of tcp connection
        :param client_keys: path for client keys. Default in None. With () it will use default file in OS
        :param str passphrase: password for encrypted client keys
        :param loop: asyncio loop object
        """
        super(Terminal, self).__init__(host=host, username=username, password=password, port=port,
                                       device_type=device_type, known_hosts=known_hosts, local_addr=local_addr,
                                       client_keys=client_keys, passphrase=passphrase, loop=loop)
        if delimeter_list is not None:
            self._delimiter_list = delimeter_list

    _delimiter_list = ['$', '#']
    """All this characters will stop reading from buffer. It mean the end of device prompt"""

    _pattern = r"[{}]"
    """Pattern for using in reading buffer. When it found processing ends"""

    async def connect(self):
        """
        Async Connection method

        General Terminal using 2 functions:

        * _establish_connection() for connecting to device
        * _set_base_prompt() for setting base pattern without setting base prompt
        """
        logger.info("Host {}: Connecting to device".format(self._host))
        await self._establish_connection()
        await self._set_base_prompt()
        logger.info("Host {}: Connected to device".format(self._host))

    async def _set_base_prompt(self):
        """Setting base pattern"""
        logger.info("Host {}: Setting base prompt".format(self._host))
        delimiters = map(re.escape, type(self)._delimiter_list)
        delimiters = r"|".join(delimiters)
        pattern = type(self)._pattern
        self._base_pattern = pattern.format(delimiters)
        logger.debug("Host {}: Base Pattern: {}".format(self._host, self._base_pattern))
        return self._base_prompt
