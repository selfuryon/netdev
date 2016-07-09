"""
Base Class for using in connection to network devices

Connection Method are based upon AsyncSSH and should be running in loop
Default params are used for Cisco

"""

import logging
import re

import asyncssh

import netdev.exceptions


class NetDev(object):
    """
    Base Class for working with network devices

    It used by default Cisco params
    """

    def __init__(self, host=u'', username=u'', password=u'', secret=u'', port=22, device_type=u'', known_hosts=None,
                 local_addr=None, client_keys=None, passphrase=None):
        """
        Initialize base class for async working with network devices

        :param host: hostname or ip address for connection
        :param username: username for logging to device
        :param password: password for user for logging to device
        :param secret: secret password for privilege mode
        :param port: ssh port for connection. Default is 22
        :param device_type: network device type. This is subclasses of this class
        :param known_hosts: file with known hosts. Default is None (no policy). with () it will use default file
        :param local_addr: local address for binding source of tcp connection
        :param client_keys: path for client keys. With () it will use default file in OS.
        :param passphrase: password for encrypted client keys
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
        self.base_prompt = self._base_pattern = ''
        self._MAX_BUFFER = 65535
        self._ansi_escape_codes = False

    def _get_default_command(self, command):
        """
        Returning default commands for device

        :param command: command for returning
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
            'check_config_mode': ')#'
        }
        # @formatter:on
        return command_mapper[command]

    @property
    def _priv_prompt_term(self):
        return '#'

    @property
    def _unpriv_prompt_term(self):
        return '>'

    async def connect(self):
        """
        Async Connection method

        Usual using 4 functions:
            establish_connection() for connecting to device
            set_base_prompt() for finding and setting device prompt
            enable() for getting privilege exec mode
            disable_paging() for non interact output in commands
        """
        await self._establish_connection()
        await self._set_base_prompt()
        await self._enable()
        await self._disable_paging()

    @property
    def _connect_params_dict(self):
        """
        Convert needed connect params to a dictionary for simplicity
        """
        return {'host': self._host, 'port': self._port, 'username': self._username, 'password': self._password,
                'known_hosts': self._known_hosts, 'local_addr': self._local_addr, 'client_keys': self._client_keys,
                'passphrase': self._passphrase}

    async def _establish_connection(self):
        """
        Establish SSH connection to the network device
        """
        output = ""
        # initiate SSH connection
        try:
            self._conn = await asyncssh.connect(**self._connect_params_dict)
        except asyncssh.DisconnectError as e:
            logging.debug("Catch asyncssh disconnect error. Code:{0}. Reason:{1}".format(e.code, e.reason))
            raise netdev.DisconnectError(self._host, e.code, e.reason)
        self._stdin, self._stdout, self._stderr = await self._conn.open_session(term_type='Dumb')
        # Flush unnecessary data
        priv_prompt = self._get_default_command('priv_prompt')
        unpriv_prompt = self._get_default_command('unpriv_prompt')
        output = await self._read_until_pattern(r"{0}|{1}".format(re.escape(priv_prompt), re.escape(unpriv_prompt)))
        logging.info("Start Connection to {0}:{1}".format(self._host, self._port))
        logging.debug("Establish Connection Output: {0}".format(output))
        return output

    async def _set_base_prompt(self):
        """
        Setting two important vars
            base_prompt - textual prompt in CLI (usually hostname)
            base_pattern - regexp for finding the end of command. It's platform specific parameter

        For Cisco devices base_pattern is "prompt(\(.*?\))?[#|>]
        """
        logging.info("In set_base_prompt")
        prompt = await self._find_prompt()
        # Strip off trailing terminator
        self.base_prompt = prompt[:-1]
        priv_prompt = self._get_default_command('priv_prompt')
        unpriv_prompt = self._get_default_command('unpriv_prompt')
        self._base_pattern = r"\w+(\(.*?\))?[{}|{}]".format(re.escape(priv_prompt), re.escape(unpriv_prompt))
        logging.debug("Base Prompt is {0}".format(self.base_prompt))
        logging.debug("Base Pattern is {0}".format(self._base_pattern))
        return self.base_prompt

    async def _disable_paging(self, command='terminal length 0'):
        """
        Disable paging method
        """
        command = self._get_default_command('disable_paging')
        command = self._normalize_cmd(command)
        logging.info("In disable_paging")
        logging.debug("Command: {}".format(command))
        self._stdin.write(command)
        output = await self._read_until_prompt()
        logging.debug("Output: {}".format(output))
        if self._ansi_escape_codes:
            output = self._strip_ansi_escape_codes(output)
        return output

    async def _find_prompt(self):
        """Finds the current network device prompt, last line only."""
        logging.info("In find_prompt")
        self._stdin.write(self._normalize_cmd("\n"))
        prompt = ''
        priv_prompt = self._get_default_command('priv_prompt')
        unpriv_prompt = self._get_default_command('unpriv_prompt')
        prompt = await self._read_until_pattern(r"{0}|{1}".format(re.escape(priv_prompt), re.escape(unpriv_prompt)))
        prompt = prompt.strip()
        if self._ansi_escape_codes:
            prompt = self._strip_ansi_escape_codes(prompt)
        if not prompt:
            raise ValueError("Unable to find prompt: {0}".format(prompt))
        logging.debug("Prompt is {0}".format(prompt))
        return prompt

    async def send_command(self, command_string, strip_command=True, strip_prompt=True):
        """
        Send command to SSH Channel

        Returns the output of the command.
        """
        logging.info('In send_command')
        output = ''
        command_string = self._normalize_cmd(command_string)
        logging.debug("Command is: {0}".format(command_string))
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

        logging.debug("Output is: {0}".format(output))
        return output

    def _strip_prompt(self, a_string):
        """
        Strip the trailing router prompt from the output
        """
        response_list = a_string.split('\n')
        last_line = response_list[-1]
        if self.base_prompt in last_line:
            return '\n'.join(response_list[:-1])
        else:
            return a_string

    async def _read_until_prompt(self):
        """Read channel until self.base_pattern detected. Return ALL data available."""
        return await self._read_until_pattern(self._base_pattern)

    async def _read_until_pattern(self, pattern='', re_flags=0):
        """Read channel until pattern detected. Return ALL data available."""
        output = ''
        logging.info("In read_until_pattern")
        if not pattern:
            pattern = self._base_pattern
        logging.debug("Pattern is: {}".format(pattern))
        while True:
            output += await self._stdout.read(self._MAX_BUFFER)
            if re.search(pattern, output, flags=re_flags):
                logging.debug("Pattern '{0}' found: {1}".format(pattern, output))
                return output

    async def _read_until_prompt_or_pattern(self, pattern='', re_flags=0):
        """Read until either self.base_pattern or pattern is detected. Return ALL data available."""
        output = ''
        logging.info("In read_until_prompt_or_pattern")
        if not pattern:
            pattern = self._base_pattern
        base_prompt_pattern = self._base_pattern
        while True:
            output += await self._stdout.read(self._MAX_BUFFER)
            if re.search(pattern, output, flags=re_flags) or re.search(base_prompt_pattern, output, flags=re_flags):
                logging.debug("Pattern '{0}' or '{1}' Found: {2}".format(pattern, base_prompt_pattern, output))
                return output

    @staticmethod
    def _strip_backspaces(output):
        """Strip any backspace characters out of the output."""
        backspace_char = '\x08'
        return output.replace(backspace_char, '')

    @staticmethod
    def _strip_command(command_string, output):
        """
        Strip command_string from output string

        Cisco IOS adds backspaces into output for long commands (i.e. for commands that line wrap)
        """
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
        """Convert '\r\r\n','\r\n', '\n\r' to '\n."""
        newline = re.compile(r'(\r\r\n|\r\n|\n\r)')
        return newline.sub('\n', a_string)

    @staticmethod
    def _normalize_cmd(command):
        """Normalize CLI commands to have a single trailing newline."""
        command = command.rstrip("\n")
        command += '\n'
        return command

    async def _check_enable_mode(self, check_string='#'):
        """Check if in enable mode. Return boolean."""
        check_string = self._get_default_command('priv_prompt')
        self._stdin.write(self._normalize_cmd('\n'))
        output = await self._read_until_prompt()
        return check_string in output

    async def _enable(self, enable_command='enable', pattern='password', re_flags=re.IGNORECASE):
        """Enter enable mode."""
        output = ""
        enable_command = self._get_default_command('priv_enter')
        if not await self._check_enable_mode():
            self._stdin.write(self._normalize_cmd(enable_command))
            output += await self._read_until_prompt_or_pattern(pattern=pattern, re_flags=re_flags)
            self._stdin.write(self._normalize_cmd(self._secret))
            output += await self._read_until_prompt()
            if not await self._check_enable_mode():
                raise ValueError("Failed to enter enable mode.")
        return output

    async def _exit_enable_mode(self, exit_enable='disable'):
        """Exit enable mode."""
        output = ""
        exit_enable = self._get_default_command('priv_exit')
        if await self._check_enable_mode():
            self._stdin.write(self._normalize_cmd(exit_enable))
            output += await self._read_until_prompt()
            if await self._check_enable_mode():
                raise ValueError("Failed to exit enable mode.")
        return output

    async def _check_config_mode(self, check_string=')#', pattern=''):
        """Checks if the device is in configuration mode or not."""
        logging.debug('In check_config_mode')
        check_string = self._get_default_command('check_config_mode')
        if not pattern:
            pattern = self._base_pattern
        self._stdin.write(self._normalize_cmd('\n'))
        output = await self._read_until_pattern(pattern=pattern)
        return check_string in output

    async def _config_mode(self, config_command='config term', pattern=''):
        """Enter into config_mode."""
        output = ''
        config_command = self._get_default_command('config_enter')
        if not pattern:
            pattern = self._base_pattern
        if not await self._check_config_mode():
            self._stdin.write(self._normalize_cmd(config_command))
            output = await self._read_until_pattern(pattern=pattern)
            if not await self._check_config_mode():
                raise ValueError("Failed to enter configuration mode.")
        return output

    async def _exit_config_mode(self, exit_config='end', pattern=''):
        """Exit from configuration mode."""
        output = ''
        exit_config = self._get_default_command('config_exit')
        if not pattern:
            pattern = self._base_pattern
        if await self._check_config_mode():
            self._stdin.write(self._normalize_cmd(exit_config))
            output = await self._read_until_pattern(pattern=pattern)
            if await self._check_config_mode():
                raise ValueError("Failed to exit configuration mode")
        return output

    async def send_config_set(self, config_commands=None, exit_config_mode=True):
        """
        Send configuration commands down the SSH channel.

        config_commands is an iterable containing all of the configuration commands.
        The commands will be executed one after the other.

        Automatically exits/enters configuration mode.
        """
        logging.info("In send_config_set")
        if config_commands is None:
            return ''
        if not hasattr(config_commands, '__iter__'):
            raise ValueError("Invalid argument passed into send_config_set")

        # Send config commands
        output = await self._config_mode()
        logging.debug("Config commands are: {0}".format(config_commands))
        for cmd in config_commands:
            self._stdin.write(self._normalize_cmd(cmd))
            output += await self._read_until_prompt()

        if exit_config_mode:
            output += await self._exit_config_mode()

        output = self._normalize_linefeeds(output)
        logging.debug("Output is {0}".format(output))
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
        logging.info("In strip_ansi_escape_codes")
        logging.debug("repr = {0}".format(repr(string_buffer)))

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

        logging.debug('new repr: {}'.format(repr(output)))
        logging.debug('new output: {}'.format(output))

        return output

    async def _cleanup(self):
        """ Any needed cleanup before closing connection """
        await self._exit_config_mode()
        self._stdin.write(self._normalize_cmd("exit"))

    async def disconnect(self):
        """ Gracefully close the SSH connection """
        await self._cleanup()
        self._conn.close()

    async def commit(self):
        """ Commit method for platforms that support this """
        raise AttributeError("Network device does not support 'commit()' method")
