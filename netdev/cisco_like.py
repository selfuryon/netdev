"""
Base Class for using in connection to network devices

Connection Method are based upon AsyncSSH and should be running in asyncio loop
"""

import re

from .base import BaseDevice
from .logger import logger


class CiscoLikeDevice(BaseDevice):
    """
    Base Class for working with network devices

    It used by default Cisco params
    """

    def __init__(self, host=u'', username=u'', password=u'', secret=u'', port=22, device_type=u'', known_hosts=None,
                 local_addr=None, client_keys=None, passphrase=None, loop=None):
        """
        Initialize base class for asynchronous working with network devices

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
        :returns: :class:`netdev.netdev_base.NetDev` Base class for working with Cisco IOS device
        """
        super().__init__(host=host, username=username, password=password, secret=secret, port=port,
                         device_type=device_type, known_hosts=known_hosts, local_addr=local_addr,
                         client_keys=client_keys, passphrase=passphrase, loop=loop)

    def _get_default_command(self, command):
        """
        Returning default commands for device

        :param str command: command for returning
        :return: real command for this network device
        """
        # @formatter:off
        command_mapper = {
            'delimeter1': '>',
            'delimeter2': '#',
            'pattern': r"{}.*?(\(.*?\))?[{}|{}]",
            'disable_paging': 'terminal length 0',
            'priv_enter': 'enable',
            'priv_exit': 'disable',
            'config_enter': 'conf t',
            'config_exit': 'end',
            'config_check': ')#',
        }
        # @formatter:on
        return command_mapper[command]

    async def connect(self):
        """
        Basic asynchronous connection method

        It connects to device and makes some preparation steps for working.
        Usual using 4 functions:

            * establish_connection() for connecting to device
            * set_base_prompt() for finding and setting device prompt
            * enable() for getting privilege exec mode
            * disable_paging() for non interact output in commands
        """
        logger.info("Host {}: Connecting to device".format(self._host))
        await self._establish_connection()
        await self._set_base_prompt()
        await self._enable()
        await self._disable_paging()
        logger.info("Host {}: Connected to device".format(self._host))

    async def _disable_paging(self):
        """Disable paging method"""
        logger.info("Host {}: Trying to disable paging".format(self._host))
        command = self._get_default_command('disable_paging')
        command = self._normalize_cmd(command)
        logger.debug("Host {}: Disable paging command: {}".format(self._host, command))
        self._stdin.write(command)
        output = await self._read_until_prompt()
        logger.debug("Host {}: Disable paging output: {}".format(self._host, output))
        if self._ansi_escape_codes:
            output = self._strip_ansi_escape_codes(output)
        return output

    async def _check_enable_mode(self):
        """Check if in enable mode. Return boolean"""
        logger.info('Host {}: Checking enable mode'.format(self._host))
        check_string = self._get_default_command('delimeter2')
        self._stdin.write(self._normalize_cmd('\n'))
        output = await self._read_until_prompt()
        return check_string in output

    async def _enable(self, pattern='password', re_flags=re.IGNORECASE):
        """Enter enable mode"""
        logger.info('Host {}: Entering to enable mode'.format(self._host))
        output = ""
        enable_command = self._get_default_command('priv_enter')
        if not await self._check_enable_mode():
            self._stdin.write(self._normalize_cmd(enable_command))
            output += await self._read_until_prompt_or_pattern(pattern=pattern, re_flags=re_flags)
            self._stdin.write(self._normalize_cmd(self._secret))
            output += await self._read_until_prompt()
            if not await self._check_enable_mode():
                raise ValueError("Failed to enter to enable mode")
        return output

    async def _exit_enable_mode(self):
        """Exit enable mode"""
        logger.info('Host {}: Exiting from enable mode'.format(self._host))
        output = ""
        exit_enable = self._get_default_command('priv_exit')
        if await self._check_enable_mode():
            self._stdin.write(self._normalize_cmd(exit_enable))
            output += await self._read_until_prompt()
            if await self._check_enable_mode():
                raise ValueError("Failed to exit from enable mode")
        return output

    async def _check_config_mode(self):
        """Checks if the device is in configuration mode or not"""
        logger.info('Host {}: Checking config mode'.format(self._host))
        check_string = self._get_default_command('config_check')
        self._stdin.write(self._normalize_cmd('\n'))
        output = await self._read_until_prompt()
        return check_string in output

    async def _config_mode(self):
        """Enter into config_mode"""
        logger.info('Host {}: Entering to config mode'.format(self._host))
        output = ''
        config_command = self._get_default_command('config_enter')
        if not await self._check_config_mode():
            self._stdin.write(self._normalize_cmd(config_command))
            output = await self._read_until_prompt()
            if not await self._check_config_mode():
                raise ValueError('Failed to enter to configuration mode')
        return output

    async def _exit_config_mode(self):
        """Exit from configuration mode"""
        logger.info('Host {}: Exiting from config mode'.format(self._host))
        output = ''
        exit_config = self._get_default_command('config_exit')
        if await self._check_config_mode():
            self._stdin.write(self._normalize_cmd(exit_config))
            output = await self._read_until_prompt()
            if await self._check_config_mode():
                raise ValueError("Failed to exit from configuration mode")
        return output

    async def send_config_set(self, config_commands=None, exit_config_mode=True):
        """
        Send configuration commands down the SSH channel.

        config_commands is an iterable containing all of the configuration commands.
        The commands will be executed one after the other.
        Automatically exits/enters configuration mode.
        :param list config_commands: piterable string list with commands for applying to network devices in conf mode
        :param Bool exit_config_mode: If true it will quit from configuration mode automatically
        :return: The output of this commands
        """

        if config_commands is None:
            return ''

        # Send config commands
        output = await self._config_mode()
        output += await super().send_config_set(config_commands=config_commands)

        if exit_config_mode:
            output += await self._exit_config_mode()

        output = self._normalize_linefeeds(output)
        logger.debug("Host {}: Config commands output: {}".format(self._host, output))
        return output

    async def _cleanup(self):
        """ Any needed cleanup before closing connection """
        logger.info("Host {}: Cleanup session".format(self._host))
        await self._exit_config_mode()
