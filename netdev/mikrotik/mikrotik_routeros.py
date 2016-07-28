import asyncssh

import netdev.exceptions
from netdev.logger import logger
from netdev.netdev_base import NetDev


class MikrotikRouterOS(NetDev):
    def __init__(self, host=u'', username=u'', password=u'', secret=u'', port=22, device_type=u'', known_hosts=None,
                 local_addr=None, client_keys=None, passphrase=None):
        """
        Invoke init with some special params (base_pattern and username)

        Mikrotik duplicate prompt in connection, so we should use pattern like
        prompt .* prompt.
        For disabling colors in CLI output we should user this username = username+c
        '+c' disables colors
        '+t' disable auto term capabilities detection
        '+80w' set terminal width to 80 rows
        """
        super(MikrotikRouterOS, self).__init__(host=host, username=username, password=password, secret=secret,
                                               port=port, device_type=device_type, known_hosts=known_hosts,
                                               local_addr=local_addr, client_keys=client_keys, passphrase=passphrase)

        self._base_pattern = r"\[.*?\] \>.*\[.*?\] \>"
        self._username += '+ct80w'
        self._ansi_escape_codes = True

    async def connect(self):
        """
        Async Connection method

        RouterOS using 2 functions:
            establish_connection() for connecting to device
            set_base_prompt() for finding and setting device prompt
            disable_paging() not needed for Mikrotik. without-paging is argument for show commands
        """
        logger.info("Connecting to device")
        await self._establish_connection()
        await self._set_base_prompt()
        logger.info("Connected to device")

    async def _establish_connection(self):
        """
        Need change the read until prompt not pattern with priv or unpriv terminators
        """
        logger.info('Establishing connection to {}:{}'.format(self._host, self._port))
        output = ""
        # initiate SSH connection
        try:
            self._conn = await asyncssh.connect(**self._connect_params_dict)
        except asyncssh.DisconnectError as e:
            logger.debug("Catch asyncssh disconnect error. Code:{0}. Reason:{1}".format(e.code, e.reason))
            raise netdev.DisconnectError(self._host, e.code, e.reason)

        self._stdin, self._stdout, self._stderr = await self._conn.open_session(term_type='dumb')
        logger.info("Connection is established to {}:{}".format(self._host, self._port))
        # Flush unnecessary data
        output = await self._read_until_prompt()
        logger.debug("Establish Connection Output: {}".format(output))
        return output

    async def _set_base_prompt(self):
        """
        Setting two important vars
            base_prompt - textual prompt in CLI (usually hostname)
            base_pattern - regexp for finding the end of command. IT's platform specific parameter

        For Mikrotik devices base_pattern is "<
        """
        logger.info("Setting base prompt")
        self._base_pattern = r"\[.*?\] (\/.*?)?\>"
        prompt = await self._find_prompt()
        user = ''
        # Strip off trailing terminator
        prompt = prompt[1:-3]
        if '@' in prompt:
            prompt = prompt.split('@')[1]
        self._base_prompt = prompt
        logger.debug("Base Prompt: {}".format(self._base_prompt))
        logger.debug("Base Pattern: {}".format(self._base_pattern))
        return self._base_prompt

    async def _find_prompt(self):
        """Finds the current network device prompt, last line only."""
        logger.info("Finding prompt")
        self._stdin.write("\r")
        prompt = ''
        prompt = await self._read_until_prompt()
        prompt = prompt.strip()
        if self._ansi_escape_codes:
            prompt = self._strip_ansi_escape_codes(prompt)
        if not prompt:
            logger.error("Unable to find prompt: {0}".format(prompt))
            raise ValueError("Unable to find prompt: {0}".format(prompt))
        logger.debug("Prompt: {0}".format(prompt))
        return prompt

    @staticmethod
    def _normalize_cmd(command):
        """Specific trailing newline for Mikrotik"""
        command = command.rstrip("\n")
        command += '\r'
        return command

    def _get_default_command(self, command):
        """
        Returning default commands for device

        :param command: command for returning
        :return: real command for this network device
        """
        # @formatter:off
        command_mapper = {
            'priv_prompt': '>',
            'unpriv_prompt': '>',
            'disable_paging': '',
            'priv_enter': '',
            'priv_exit': '',
            'config_enter': '',
            'config_exit': '',
            'check_config_mode': '>'
        }
        # @formatter:on
        return command_mapper[command]

    async def _cleanup(self):
        """ Don't need anything """
        pass

    async def send_config_set(self, config_commands=None, exit_config_mode=False):
        """
        Send configuration commands down the SSH channel.

        config_commands is an iterable containing all of the configuration commands.
        The commands will be executed one after the other.
        Automatically exits/enters configuration mode.
        :param list config_commands: piterable string list with commands for applying to network devices in conf mode
        :param Bool exit_config_mode: If true it will quit from configuration mode automatically
        :return: The output of this commands
        """
        logger.info("Sending configuration settings")
        if config_commands is None:
            return ''
        if not hasattr(config_commands, '__iter__'):
            raise ValueError("Invalid argument passed into send_config_set")

        # Send config commands
        output = ''
        logger.debug("Config commands: {}".format(config_commands))
        for cmd in config_commands:
            output += await self.send_command(cmd, strip_command=False, strip_prompt=False)

        output = self._normalize_linefeeds(output)
        logger.debug("Config commands output: {}".format(output))
        return output
