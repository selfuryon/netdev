"""
CiscoLikeDevice Class is abstract class for using in cisco like devices

Connection Method are based upon AsyncSSH and should be running in asyncio loop
"""

import re

from .base import BaseDevice
from .logger import logger


class IOSLikeDevice(BaseDevice):
    """
    This Class is abstract class for working with cisco like devices

    Cisco like devices having several concepts:

    * user exec or unprivilege exec. This mode allows you perform basic tests and get system information.
    * privilage exec. This mode allows the use of all EXEC mode commands available on the system
    * configuration mode or config mode. This mode are used for configuration whole system.
    """

    def __init__(self, host=u'', username=u'', password=u'', secret=u'', port=22, device_type=u'', known_hosts=None,
                 local_addr=None, client_keys=None, passphrase=None, loop=None):
        """
        Initialize class for asynchronous working with network devices

        :param str host: hostname or ip address for connection
        :param str username: username for logger to device
        :param str password: password for user for logger to device
        :param str secret: secret password for privilege mode
        :param int port: ssh port for connection. Default is 22
        :param str device_type: network device type. This is subclasses of this class
        :param known_hosts: file with known hosts. Default is None (no policy). with () it will use default file
        :param str local_addr: local address for binding source of tcp connection
        :param client_keys: path for client keys. With () it will use default file in OS.
        :param str passphrase: password for encrypted client keys
        :param loop: asyncio loop object
        :returns: :class:`IOSLikeDevice` class for working with devices like Cisco
        """
        super().__init__(host=host, username=username, password=password, secret=secret, port=port,
                         device_type=device_type, known_hosts=known_hosts, local_addr=local_addr,
                         client_keys=client_keys, passphrase=passphrase, loop=loop)

    _priv_enter = 'enable'
    _priv_exit = 'disable'
    _priv_check = '#'
    _config_enter = 'conf t'
    _config_exit = 'end'
    _config_check = ')#'

    async def connect(self):
        """
        Basic asynchronous connection method

        It connects to device and makes some preparation steps for working with cisco like devices
        Usual using 4 functions:

        * _establish_connection() for connecting to device
        * _set_base_prompt() for finding and setting device prompt
        * _enable() for getting privilege exec mode
        * _disable_paging() for non interact output in commands
        """
        logger.info("Host {}: Connecting to device".format(self._host))
        await self._establish_connection()
        await self._set_base_prompt()
        await self.enable_mode()
        await self._disable_paging()
        logger.info("Host {}: Connected to device".format(self._host))

    async def check_enable_mode(self):
        """Check if in enable mode. Return boolean"""
        logger.info('Host {}: Checking enable mode'.format(self._host))
        check_string = type(self)._priv_check
        self._stdin.write(self._normalize_cmd('\n'))
        output = await self._read_until_prompt()
        return check_string in output

    async def enable_mode(self, pattern='password', re_flags=re.IGNORECASE):
        """Enter enable mode"""
        logger.info('Host {}: Entering to enable mode'.format(self._host))
        output = ""
        enable_command = type(self)._priv_enter
        if not await self.check_enable_mode():
            self._stdin.write(self._normalize_cmd(enable_command))
            output += await self._read_until_prompt_or_pattern(pattern=pattern, re_flags=re_flags)
            if re.search(pattern, output, re_flags):
                self._stdin.write(self._normalize_cmd(self._secret))
                output += await self._read_until_prompt()
            if not await self.check_enable_mode():
                raise ValueError("Failed to enter to enable mode")
        return output

    async def exit_enable_mode(self):
        """Exit enable mode"""
        logger.info('Host {}: Exiting from enable mode'.format(self._host))
        output = ""
        exit_enable = type(self)._priv_exit
        if await self.check_enable_mode():
            self._stdin.write(self._normalize_cmd(exit_enable))
            output += await self._read_until_prompt()
            if await self.check_enable_mode():
                raise ValueError("Failed to exit from enable mode")
        return output

    async def check_config_mode(self):
        """Checks if the device is in configuration mode or not"""
        logger.info('Host {}: Checking config mode'.format(self._host))
        check_string = type(self)._config_check
        self._stdin.write(self._normalize_cmd('\n'))
        output = await self._read_until_prompt()
        return check_string in output

    async def config_mode(self):
        """Enter into config_mode"""
        logger.info('Host {}: Entering to config mode'.format(self._host))
        output = ''
        config_command = type(self)._config_enter
        if not await self.check_config_mode():
            self._stdin.write(self._normalize_cmd(config_command))
            output = await self._read_until_prompt()
            if not await self.check_config_mode():
                raise ValueError('Failed to enter to configuration mode')
        return output

    async def exit_config_mode(self):
        """Exit from configuration mode"""
        logger.info('Host {}: Exiting from config mode'.format(self._host))
        output = ''
        exit_config = type(self)._config_exit
        if await self.check_config_mode():
            self._stdin.write(self._normalize_cmd(exit_config))
            output = await self._read_until_prompt()
            if await self.check_config_mode():
                raise ValueError("Failed to exit from configuration mode")
        return output

    async def send_config_set(self, config_commands=None, exit_config_mode=True):
        """
        Sending configuration commands to cisco like devices

        The commands will be executed one after the other.
        Automatically exits/enters configuration mode.

        :param list config_commands: iterable string list with commands for applying to network devices in conf mode
        :param bool exit_config_mode: If true it will quit from configuration mode automatically
        :return: The output of this commands
        """

        if config_commands is None:
            return ''

        # Send config commands
        output = await self.config_mode()
        output += await super().send_config_set(config_commands=config_commands)

        if exit_config_mode:
            output += await self.exit_config_mode()

        output = self._normalize_linefeeds(output)
        logger.debug("Host {}: Config commands output: {}".format(self._host, repr(output)))
        return output

    async def _cleanup(self):
        """ Any needed cleanup before closing connection """
        logger.info("Host {}: Cleanup session".format(self._host))
        await self.exit_config_mode()
