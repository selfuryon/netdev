"""
Base Class for using in connection to network devices

Connection Method are based upon AsyncSSH and should be running in asyncio loop
"""

import re

from .base import BaseDevice
from .logger import logger


class HPLikeDevice(BaseDevice):
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
            'delimeter2': ']',
            'delimeter_left1': '<',
            'delimeter_left2': '[',
            'pattern': r"[{}|{}]{}[\-\w]*[{}|{}]",
            'disable_paging': 'screen-length disable',
            'sview_enter': 'system-view',
            'sview_exit': 'return',
            'sview_check': ']'
        }
        # @formatter:on
        return command_mapper[command]

    async def _set_base_prompt(self):
        """
        Setting two important vars
            base_prompt - textual prompt in CLI (usually hostname)
            base_pattern - regexp for finding the end of command. IT's platform specific parameter

        For Comware devices base_pattern is "[\]|>]prompt(\-\w+)?[\]|>]
        """
        logger.info("Host {}: Setting base prompt".format(self._host))
        prompt = await self._find_prompt()
        # Strip off trailing terminator
        self._base_prompt = prompt[1:-1]
        delimeter1 = self._get_default_command('delimeter1')
        delimeter2 = self._get_default_command('delimeter2')
        delimeter_left1 = self._get_default_command('delimeter_left1')
        delimeter_left2 = self._get_default_command('delimeter_left2')
        pattern = self._get_default_command('pattern')
        self._base_pattern = pattern.format(re.escape(delimeter_left1), re.escape(delimeter_left2),
                                            re.escape(self._base_prompt[:12]), re.escape(delimeter1),
                                            re.escape(delimeter2))
        logger.debug("Host {}: Base Prompt: {}".format(self._host, self._base_prompt))
        logger.debug("Host {}: Base Pattern: {}".format(self._host, self._base_pattern))
        return self._base_prompt

    async def _check_sview(self):
        """Check if in system-view mode. Return boolean"""
        logger.info('Host {}: Checking system-view mode'.format(self._host))
        check_string = self._get_default_command('sview_check')
        self._stdin.write(self._normalize_cmd('\n'))
        output = await self._read_until_prompt()
        return check_string in output

    async def _sview(self, pattern='password', re_flags=re.IGNORECASE):
        """Enter system-view mode"""
        logger.info('Host {}: Entering to system-view mode'.format(self._host))
        output = ""
        sview_enter = self._get_default_command('sview_enter')
        if not await self._check_sview():
            self._stdin.write(self._normalize_cmd(sview_enter))
            output += await self._read_until_prompt_or_pattern(pattern=pattern, re_flags=re_flags)
            if re.match(pattern, output, re_flags):
                self._stdin.write(self._normalize_cmd(self._secret))
                output += await self._read_until_prompt()
            if not await self._check_sview():
                raise ValueError("Failed to enter to system-view mode")
        return output

    async def _exit_sview(self):
        """Exit system-view mode"""
        logger.info('Host {}: Exiting from system-view mode'.format(self._host))
        output = ""
        sview_exit = self._get_default_command('sview_exit')
        if await self._check_sview():
            self._stdin.write(self._normalize_cmd(sview_exit))
            output += await self._read_until_prompt()
            if await self._check_sview():
                raise ValueError("Failed to exit from system-view mode")
        return output

    async def send_config_set(self, config_commands=None, exit_sview_mode=False):
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
        output = await self._sview()
        output += await super().send_config_set(config_commands=config_commands)

        if exit_sview_mode:
            output += await self._exit_sview()

        output = self._normalize_linefeeds(output)
        logger.debug("Host {}: Config commands output: {}".format(self._host, output))
        return output
