"""
Base Class for using in connection to network devices

Connection Method are based upon AsyncSSH and should be running in asyncio loop
"""

import re

import asyncssh

from .exceptions import DisconnectError
from .logger import logger


class NetDev(object):
    """
    Base Class for working with network devices

    It used by default Cisco params
    """

    def __init__(self, host=u'', username=u'', password=u'', secret=u'', port=22, device_type=u'', known_hosts=None,
                 local_addr=None, client_keys=None, passphrase=None):
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
        if host:
            self._host = host
        else:
            raise ValueError("Host must be set")
        self._port = int(port)
        self._username = username
        self._password = password
        self._secret = secret
        self._device_type = device_type
        self._known_hosts = known_hosts
        self._local_addr = local_addr
        self._client_keys = client_keys
        self._passphrase = passphrase

        # Filling internal vars
        self._stdin = self._stdout = self._stderr = self._conn = None
        self._base_prompt = self._base_pattern = ''
        self._MAX_BUFFER = 65535
        self._ansi_escape_codes = False

    @property
    def base_prompt(self):
        """ Returning base prompt for this network device"""
        return self._base_prompt

    def _get_default_command(self, command):
        """
        Returning default commands for device

        :param str command: command for returning
        :return: real command for this network device
        """
        # @formatter:off
        command_mapper = {
            'priv_prompt': '#',
            'unpriv_prompt': '>',
            'disable_paging': 'terminal length 0',
            'priv_enter': 'enable',
            'priv_exit': 'disable',
            'config_enter': 'conf t',
            'config_exit': 'end',
            'check_config_mode': ')#',
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

    @property
    def _connect_params_dict(self):
        """Convert needed connect params to a dictionary for simplicity"""
        # @formatter:off
        return {'host': self._host,
                'port': self._port,
                'username': self._username,
                'password': self._password,
                'known_hosts': self._known_hosts,
                'local_addr': self._local_addr,
                'client_keys': self._client_keys,
                'passphrase': self._passphrase}
        # @formatter:on

    async def _establish_connection(self):
        """Establish SSH connection to the network device"""
        logger.info('Host {}: Establishing connection to port {}'.format(self._host, self._port))
        output = ""
        # initiate SSH connection
        try:
            self._conn = await asyncssh.connect(**self._connect_params_dict)
        except asyncssh.DisconnectError as e:
            raise DisconnectError(self._host, e.code, e.reason)
        self._stdin, self._stdout, self._stderr = await self._conn.open_session(term_type='Dumb')
        logger.info("Host {}: Connection is established".format(self._host))
        # Flush unnecessary data
        priv_prompt = self._get_default_command('priv_prompt')
        unpriv_prompt = self._get_default_command('unpriv_prompt')
        output = await self._read_until_pattern(r"{}|{}".format(re.escape(priv_prompt), re.escape(unpriv_prompt)))
        logger.debug("Host {}: Establish Connection Output: {}".format(self._host, output))
        return output

    async def _set_base_prompt(self):
        """
        Setting two important vars:

            base_prompt - textual prompt in CLI (usually hostname)
            base_pattern - regexp for finding the end of command. It's platform specific parameter

        For Cisco devices base_pattern is "prompt(\(.*?\))?[#|>]
        """
        logger.info("Host {}: Setting base prompt".format(self._host))
        prompt = await self._find_prompt()
        # Strip off trailing terminator
        self._base_prompt = prompt[:-1]
        priv_prompt = self._get_default_command('priv_prompt')
        unpriv_prompt = self._get_default_command('unpriv_prompt')
        self._base_pattern = r"{}.*?(\(.*?\))?[{}|{}]".format(re.escape(self._base_prompt[:12]), re.escape(priv_prompt),
                                                              re.escape(unpriv_prompt))
        logger.debug("Host {}: Base Prompt: {}".format(self._host, self._base_prompt))
        logger.debug("Host {}: Base Pattern: {}".format(self._host, self._base_pattern))
        return self._base_prompt

    async def _disable_paging(self):
        """Disable paging method"""
        logger.info("Host {}: Trying disable paging".format(self._host))
        command = self._get_default_command('disable_paging')
        command = self._normalize_cmd(command)
        logger.debug("Host {}: Disable paging command: {}".format(self._host, command))
        self._stdin.write(command)
        output = await self._read_until_prompt()
        logger.debug("Host {}: Disable paging output: {}".format(self._host, output))
        if self._ansi_escape_codes:
            output = self._strip_ansi_escape_codes(output)
        return output

    async def _find_prompt(self):
        """Finds the current network device prompt, last line only"""
        logger.info("Host {}: Finding prompt".format(self._host))
        self._stdin.write(self._normalize_cmd("\n"))
        prompt = ''
        priv_prompt = self._get_default_command('priv_prompt')
        unpriv_prompt = self._get_default_command('unpriv_prompt')
        prompt = await self._read_until_pattern(r"{0}|{1}".format(re.escape(priv_prompt), re.escape(unpriv_prompt)))
        prompt = prompt.strip()
        if self._ansi_escape_codes:
            prompt = self._strip_ansi_escape_codes(prompt)
        if not prompt:
            raise ValueError("Host {}: Unable to find prompt: {}".format(self._host, prompt))
        logger.debug("Host {}: Prompt: {}".format(self._host, prompt))
        return prompt

    async def send_command(self, command_string, strip_command=True, strip_prompt=True):
        """
        Send command to SSH Channel

        :param str command_string: command for executing basically in privilege mode
        :param bool strip_command: True or False for stripping command from output
        :param bool strip_prompt: True or False for stripping ending device prompt
        :return: The output of the command
        """
        logger.info('Host {}: Sending command'.format(self._host))
        output = ''
        command_string = self._normalize_cmd(command_string)
        logger.debug("Host {}: Send command: {}".format(self._host, command_string))
        self._stdin.write(command_string)
        output = await self._read_until_prompt()

        # Some platforms have ansi_escape codes
        if self._ansi_escape_codes:
            output = self._strip_ansi_escape_codes(output)
        output = self._normalize_linefeeds(output)
        if strip_prompt:
            output = self._strip_prompt(output)
        if strip_command:
            output = self._strip_command(command_string, output)

        logger.debug("Host {}: Send command output: {}".format(self._host, output))
        return output

    def _strip_prompt(self, a_string):
        """Strip the trailing router prompt from the output"""
        logger.info('Host {}: Stripping prompt'.format(self._host))
        response_list = a_string.split('\n')
        last_line = response_list[-1]
        if self._base_prompt in last_line:
            return '\n'.join(response_list[:-1])
        else:
            return a_string

    async def _read_until_prompt(self):
        """Read channel until self.base_pattern detected. Return ALL data available"""
        return await self._read_until_pattern(self._base_pattern)

    async def _read_until_pattern(self, pattern='', re_flags=0):
        """Read channel until pattern detected. Return ALL data available"""
        output = ''
        logger.info("Host {}: Reading until pattern".format(self._host))
        if not pattern:
            pattern = self._base_pattern
        logger.debug("Host {}: Reading pattern: {}".format(self._host, pattern))
        while True:
            output += await self._stdout.read(self._MAX_BUFFER)
            if re.search(pattern, output, flags=re_flags):
                logger.debug("Host {}: Reading pattern '{}' was found: {}".format(self._host, pattern, output))
                return output

    async def _read_until_prompt_or_pattern(self, pattern='', re_flags=0):
        """Read until either self.base_pattern or pattern is detected. Return ALL data available"""
        output = ''
        logger.info("Host {}: Reading until prompt or pattern".format(self._host))
        if not pattern:
            pattern = self._base_pattern
        base_prompt_pattern = self._base_pattern
        while True:
            output += await self._stdout.read(self._MAX_BUFFER)
            if re.search(pattern, output, flags=re_flags) or re.search(base_prompt_pattern, output, flags=re_flags):
                logger.debug("Host {}: Reading pattern '{}' or '{}' was found: {}".format(self._host, pattern,
                                                                                          base_prompt_pattern, output))
                return output

    @staticmethod
    def _strip_backspaces(output):
        """Strip any backspace characters out of the output"""
        backspace_char = '\x08'
        return output.replace(backspace_char, '')

    @staticmethod
    def _strip_command(command_string, output):
        """
        Strip command_string from output string

        Cisco IOS adds backspaces into output for long commands (i.e. for commands that line wrap)
        """
        logger.info('Stripping command')
        backspace_char = '\x08'

        # Check for line wrap (remove backspaces)
        if backspace_char in output:
            output = output.replace(backspace_char, '')
            output_lines = output.split("\n")
            new_output = output_lines[1:]
            return "\n".join(new_output)
        else:
            command_length = len(command_string)
            return output[command_length:]

    @staticmethod
    def _normalize_linefeeds(a_string):
        """Convert '\r\r\n','\r\n', '\n\r' to '\n"""
        newline = re.compile(r'(\r\r\n|\r\n|\n\r)')
        return newline.sub('\n', a_string)

    @staticmethod
    def _normalize_cmd(command):
        """Normalize CLI commands to have a single trailing newline"""
        command = command.rstrip("\n")
        command += '\n'
        return command

    async def _check_enable_mode(self):
        """Check if in enable mode. Return boolean"""
        logger.info('Host {}: Checking enable mode'.format(self._host))
        check_string = self._get_default_command('priv_prompt')
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

    async def _check_config_mode(self, pattern=''):
        """Checks if the device is in configuration mode or not"""
        logger.info('Host {}: Checking config mode'.format(self._host))
        check_string = self._get_default_command('check_config_mode')
        if not pattern:
            pattern = self._base_pattern
        self._stdin.write(self._normalize_cmd('\n'))
        output = await self._read_until_pattern(pattern=pattern)
        return check_string in output

    async def _config_mode(self, pattern=''):
        """Enter into config_mode"""
        logger.info('Host {}: Entering to config mode'.format(self._host))
        output = ''
        config_command = self._get_default_command('config_enter')
        if not pattern:
            pattern = self._base_pattern
        if not await self._check_config_mode():
            self._stdin.write(self._normalize_cmd(config_command))
            output = await self._read_until_pattern(pattern=pattern)
            if not await self._check_config_mode():
                raise ValueError('Failed to enter to configuration mode')
        return output

    async def _exit_config_mode(self, pattern=''):
        """Exit from configuration mode"""
        logger.info('Host {}: Exiting from config mode'.format(self._host))
        output = ''
        exit_config = self._get_default_command('config_exit')
        if not pattern:
            pattern = self._base_pattern
        if await self._check_config_mode():
            self._stdin.write(self._normalize_cmd(exit_config))
            output = await self._read_until_pattern(pattern=pattern)
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
        logger.info("Host {}: Sending configuration settings".format(self._host))
        if config_commands is None:
            return ''
        if not hasattr(config_commands, '__iter__'):
            raise ValueError("Host {}: Invalid argument passed into send_config_set".format(self._host))

        # Send config commands
        output = await self._config_mode()
        logger.debug("Host {}: Config commands: {}".format(self._host, config_commands))
        for cmd in config_commands:
            self._stdin.write(self._normalize_cmd(cmd))
            output += await self._read_until_prompt()

        if exit_config_mode:
            output += await self._exit_config_mode()

        output = self._normalize_linefeeds(output)
        logger.debug("Host {}: Config commands output: {}".format(self._host, output))
        return output

    @staticmethod
    def _strip_ansi_escape_codes(string_buffer):
        """
        Remove some ANSI ESC codes from the output

        http://en.wikipedia.org/wiki/ANSI_escape_code

        Note: this does not capture ALL possible ANSI Escape Codes only the ones
        I have encountered

        Current codes that are filtered:
        ESC = '\x1b' or chr(27)
        ESC = is the escape character [^ in hex ('\x1b')
        ESC[24;27H   Position cursor
        ESC[?25h     Show the cursor
        ESC[E        Next line (HP does ESC-E)
        ESC[2K       Erase line
        ESC[1;24r    Enable scrolling from start to row end
        ESC7         Save cursor position
        ESC[r        Scroll all screen
        ESC8         Restore cursor position
        ESC[nA       Move cursor up to n cells
        ESC[nB       Move cursor down to n cells

        require:
            HP ProCurve
            F5 LTM's
            Mikrotik
        """
        logger.info("Stripping ansi escape codes")
        logger.debug("Old repr: {}".format(repr(string_buffer)))

        code_save_cursor = chr(27) + r'7'
        code_scroll_screen = chr(27) + r'\[r'
        code_restore_cursor = chr(27) + r'8'
        code_cursor_up = chr(27) + r'\[\d+A'
        code_cursor_down = chr(27) + r'\[\d+B'

        code_position_cursor = chr(27) + r'\[\d+;\d+H'
        code_show_cursor = chr(27) + r'\[\?25h'
        code_next_line = chr(27) + r'E'
        code_erase_line = chr(27) + r'\[2K'
        code_enable_scroll = chr(27) + r'\[\d+;\d+r'

        code_set = [code_save_cursor, code_scroll_screen, code_restore_cursor, code_cursor_up, code_cursor_down,
                    code_position_cursor, code_show_cursor, code_erase_line, code_enable_scroll]

        output = string_buffer
        for ansi_esc_code in code_set:
            output = re.sub(ansi_esc_code, '', output)

        # CODE_NEXT_LINE must substitute with '\n'
        output = re.sub(code_next_line, '\n', output)

        logger.debug('New repr: {}'.format(repr(output)))
        logger.debug('Stripped output: {}'.format(output))

        return output

    async def _cleanup(self):
        """ Any needed cleanup before closing connection """
        logger.info("Host {}: Cleanup session".format(self._host))
        await self._exit_config_mode()

    async def disconnect(self):
        """ Gracefully close the SSH connection """
        logger.info("Host {}: Disconnecting".format(self._host))
        await self._cleanup()
        self._conn.close()

