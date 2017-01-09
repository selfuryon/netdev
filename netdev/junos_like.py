"""
JunOSLikeDevice Class is abstract class for using in Juniper JunOS like devices

Connection Method are based upon AsyncSSH and should be running in asyncio loop
"""

import re

from .base import BaseDevice
from .logger import logger


class JunOSLikeDevice(BaseDevice):
    """
    This Class for working with Juniper JunOS like devices

    Juniper JunOS like devices having several concepts:

    * bsd shell (csh). This is csh shell for FreeBSD. This mode is not covered by this Class.
    * operation mode. This mode is using for getting information from device
    * configuration mode. This mode is using for configuration system
    """

    def __init__(self, host=u'', username=u'', password=u'', secret=u'', port=22, device_type=u'', known_hosts=None,
                 local_addr=None, client_keys=None, passphrase=None, loop=None):
        """
        Initialize  class for asynchronous working with network devices

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
        :returns: :class:`ComwareLikeDevice` Base class for working with hp comware like devices
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
            'delimeter0': '%',
            'delimeter1': '>',
            'delimeter2': '#',
            'pattern': r"\w+(\@[\-\w]*)?[{}|{}]",
            'disable_paging': 'set cli screen-length 0',
            'config_enter': 'configure',
            'config_exit': 'exit configuration-mode',
            'config_check': '#'
        }
        # @formatter:on
        return command_mapper[command]

    async def _set_base_prompt(self):
        """
        Setting two important vars
            base_prompt - textual prompt in CLI (usually username or hostname)
            base_pattern - regexp for finding the end of command. IT's platform specific parameter

        For JunOS devices base_pattern is "user(@[hostname])?[>|#]
        """
        logger.info("Host {}: Setting base prompt".format(self._host))
        prompt = await self._find_prompt()
        prompt = prompt[:-1]
        # Strip off trailing terminator
        if '@' in prompt:
            prompt = prompt.split('@')[1]
        self._base_prompt = prompt
        pattern = self._get_default_command('pattern')
        delimeter1 = self._get_default_command('delimeter1')
        delimeter2 = self._get_default_command('delimeter2')
        self._base_pattern = pattern.format(re.escape(delimeter1), re.escape(delimeter2))
        logger.debug("Host {}: Base Prompt: {}".format(self._host, self._base_prompt))
        logger.debug("Host {}: Base Pattern: {}".format(self._host, self._base_pattern))
        return self._base_prompt

    async def _check_config_mode(self):
        """Check if in configuration mode. Return boolean"""
        logger.info('Host {}: Checking configuration mode'.format(self._host))
        check_string = self._get_default_command('config_check')
        self._stdin.write(self._normalize_cmd('\n'))
        output = await self._read_until_prompt()
        return check_string in output

    async def _config(self):
        """Enter configuration mode"""
        logger.info('Host {}: Entering to configuration mode'.format(self._host))
        output = ""
        config_enter = self._get_default_command('config_enter')
        if not await self._check_config_mode():
            self._stdin.write(self._normalize_cmd(config_enter))
            output += await self._read_until_prompt()
            if not await self._check_config_mode():
                raise ValueError("Failed to enter to configuration mode")
        return output

    async def _exit_config_mode(self):
        """Exit system-view mode. It doesn't exit from configuration mode if system has uncommitted changes"""
        logger.info('Host {}: Exiting from configuration mode'.format(self._host))
        output = ""
        config_exit = self._get_default_command('config_exit')
        if await self._check_config_mode():
            self._stdin.write(self._normalize_cmd(config_exit))
            output += await self._read_until_prompt()
            if await self._check_config_mode():
                raise ValueError("Failed to exit from configuration mode")
        return output

    async def send_config_set(self, config_commands=None, with_commit=True, commit_comment='', exit_config_mode=True):
        """
        Sending configuration commands to device

        The commands will be executed one after the other.
        Automatically exits/enters configuration mode.

        :param list config_commands: iterable string list with commands for applying to network devices in system view
        :param bool with_commit: if true it commit all changes after applying all config_commands
        :param string commit_comment: message for configuration commit
        :param bool exit_config_mode: If true it will quit from configuration mode automatically
        :return: The output of these commands
        """

        if config_commands is None:
            return ''

        # Send config commands
        output = await self._config()
        output += await super().send_config_set(config_commands=config_commands)

        if with_commit:
            if commit_comment:
                commit = "commit comment {}".format(commit_comment)
                self._stdin.write(self._normalize_cmd(commit))
            else:
                self._stdin.write(self._normalize_cmd("commit"))

            output += await self._read_until_prompt()

        if exit_config_mode:
            output += await self._exit_config_mode()

        output = self._normalize_linefeeds(output)
        logger.debug("Host {}: Config commands output: {}".format(self._host, output))
        return output
