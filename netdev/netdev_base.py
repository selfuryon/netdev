"""
Base Class for using in connection to network devices

Connection Method are based upon AsyncSSH and should be running in loop
Default params are used for Cisco

"""

import logging
import re

import asyncssh


class NetDevSSH(object):
    """
    Base Class for working with network devices

    It used default Cisco params
    """

    def __init__(self, ip=u'', host=u'', username=u'', password=u'', secret=u'', port=22, device_type=u'',
                 ssh_strict=False):
        # Filling vars
        if ip:
            self._host = ip
            self._ip = ip
        elif host:
            self._host = host
        if not ip and not host:
            raise ValueError("Either ip or host must be set")
        self._port = int(port)
        self._username = username
        self._password = password
        self._secret = secret
        self._device_type = device_type
        if ssh_strict:
            self._key_policy = ()
        else:
            self._key_policy = None

        # Filling internal vars
        self._stdin = self._stdout = self._stderr = self._conn = ''
        self._base_prompt = self._base_pattern = ''
        self._MAX_BUFFER = 65535
        self._ansi_escape_codes = False

    @property
    def priv_prompt_term(self):
        return '#'

    @property
    def unpriv_prompt_term(self):
        return '>'

    async def connect(self):
        """
        Async Connection method

        Usual using 3 functions:
            establish_connection for connecting to device
            set_base_prompt for finding and setting device prompt
            disable_paging for non interact output in commands
        """
        await self.establish_connection()
        await self.set_base_prompt()
        await self.enable()
        await self.disable_paging()

    @property
    def connect_params_dict(self):
        """
        Convert needed connect params to a dictionary for simplicity
        """
        return {'host': self._host, 'port': self._port, 'username': self._username, 'password': self._password,
                'known_hosts': self._key_policy}

    async def establish_connection(self):
        """
        Establish SSH connection to the network device
        """
        output = ""
        # initiate SSH connection
        self._conn = await asyncssh.connect(**self.connect_params_dict)
        self._stdin, self._stdout, self._stderr = await self._conn.open_session(term_type='vt100')
        # Flush unnecessary data
        output = await self.read_until_pattern(
            r"{0}|{1}".format(re.escape(self.priv_prompt_term), re.escape(self.unpriv_prompt_term)))
        logging.info("Start Connection to {0}:{1}".format(self._host, self._port))
        logging.info("Establish Connection Output {0}".format(output))
        return output

    async def set_base_prompt(self):
        """
        Setting two important vars
            base_prompt - textual prompt in CLI (usually hostname)
            base_pattern - regexp for finding the end of command. IT's platform specific parameter

        For Cisco devices base_pattern is "prompt(\(.*?\))?[#|>]
        """
        logging.info("In set_base_prompt")
        prompt = await self.find_prompt()
        # Strip off trailing terminator
        self._base_prompt = prompt[:-1]
        self._base_pattern = self.prompt_pattern.format(re.escape(self._base_prompt), re.escape(self.priv_prompt_term),
                                                        re.escape(self.unpriv_prompt_term))
        logging.debug("Base Prompt is {0}".format(self._base_prompt))
        logging.debug("Base Pattern is {0}".format(self._base_pattern))
        return self._base_prompt

    @property
    def prompt_pattern(self):
        return r"{0}(\(.*?\))?[{1}|{2}]"

    async def disable_paging(self):
        """
        Disable paging method
        """
        command = self.normalize_cmd(self.disable_paging_command)
        logging.info("In disable_paging")
        logging.debug("Command: {}".format(command))
        self._stdin.write(command)
        output = await self.read_until_prompt()
        logging.debug("Output: {}".format(output))
        if self._ansi_escape_codes:
            output = self.strip_ansi_escape_codes(output)
        return output

    @property
    def disable_paging_command(self):
        return "terminal length 0"

    async def find_prompt(self):
        """Finds the current network device prompt, last line only."""
        logging.info("In find_prompt")
        self._stdin.write("\n")
        prompt = ''
        prompt = await self.read_until_pattern(
            r"{0}|{1}".format(re.escape(self.priv_prompt_term), re.escape(self.unpriv_prompt_term)))
        prompt = prompt.strip()
        if self._ansi_escape_codes:
            prompt = self.strip_ansi_escape_codes(prompt)
        if not prompt:
            raise ValueError("Unable to find prompt: {0}".format(prompt))
        logging.debug("Prompt is {0}".format(prompt))
        return prompt

    async def send_command(self, command_string, strip_prompt=True, strip_command=True):
        """
        Send command to SSH Channel

        Returns the output of the command.
        """
        logging.info('In send_command')
        output = ''
        command_string = self.normalize_cmd(command_string)
        logging.debug("Command is: {0}".format(command_string))
        self._stdin.write(command_string)
        output = await self.read_until_prompt()

        # Some platforms have ansi_escape codes
        if self._ansi_escape_codes:
            output = self.strip_ansi_escape_codes(output)
        output = self.normalize_linefeeds(output)
        if strip_command:
            output = self.strip_command(command_string, output)
        if strip_prompt:
            output = self.strip_prompt(output)

        logging.debug("Output is: {0}".format(output))
        return output

    def strip_prompt(self, a_string):
        """
        Strip the trailing router prompt from the output
        """
        response_list = a_string.split('\n')
        last_line = response_list[-1]
        if self._base_prompt in last_line:
            return '\n'.join(response_list[:-1])
        else:
            return a_string

    async def read_until_prompt(self):
        """Read channel until self.base_pattern detected. Return ALL data available."""
        return await self.read_until_pattern(self._base_pattern)

    async def read_until_pattern(self, pattern='', re_flags=0):
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

    async def read_until_prompt_or_pattern(self, pattern='', re_flags=0):
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
    def strip_backspaces(output):
        """Strip any backspace characters out of the output."""
        backspace_char = '\x08'
        return output.replace(backspace_char, '')

    @staticmethod
    def strip_command(command_string, output):
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
    def normalize_linefeeds(a_string):
        """Convert '\r\r\n','\r\n', '\n\r' to '\n."""
        newline = re.compile(r'(\r\r\n|\r\n|\n\r)')
        return newline.sub('\n', a_string)

    @staticmethod
    def normalize_cmd(command):
        """Normalize CLI commands to have a single trailing newline."""
        command = command.rstrip("\n")
        command += '\n'
        return command

    async def check_enable_mode(self, check_string='#'):
        """Check if in enable mode. Return boolean."""
        self._stdin.write('\n')
        output = await self.read_until_prompt()
        return check_string in output

    async def enable(self, enable_command='enable', pattern='password', re_flags=re.IGNORECASE):
        """Enter enable mode."""
        output = ""
        if not await self.check_enable_mode():
            self._stdin.write(self.normalize_cmd(enable_command))
            output += await self.read_until_prompt_or_pattern(pattern=pattern, re_flags=re_flags)
            self._stdin.write(self.normalize_cmd(self._secret))
            output += await self.read_until_prompt()
            if not await self.check_enable_mode():
                raise ValueError("Failed to enter enable mode.")
        return output

    async def exit_enable_mode(self, exit_enable='disable'):
        """Exit enable mode."""
        output = ""
        if await self.check_enable_mode():
            self._stdin.write(self.normalize_cmd(exit_enable))
            output += await self.read_until_prompt()
            if await self.check_enable_mode():
                raise ValueError("Failed to exit enable mode.")
        return output

    async def check_config_mode(self, check_string=')#', pattern=''):
        """Checks if the device is in configuration mode or not."""
        if not pattern:
            pattern = self._base_pattern
        self._stdin.write('\n')
        output = await self.read_until_pattern(pattern=pattern)
        return check_string in output

    async def config_mode(self, config_command='config term', pattern=''):
        """Enter into config_mode."""
        output = ''
        if not pattern:
            pattern = self._base_pattern
        if not await self.check_config_mode():
            self._stdin.write(self.normalize_cmd(config_command))
            output = await self.read_until_pattern(pattern=pattern)
            if not await self.check_config_mode():
                raise ValueError("Failed to enter configuration mode.")
        return output

    async def exit_config_mode(self, exit_config='end', pattern=''):
        """Exit from configuration mode."""
        output = ''
        if not pattern:
            pattern = self._base_pattern
        if await self.check_config_mode():
            self._stdin.write(self.normalize_cmd(exit_config))
            output = await self.read_until_pattern(pattern=pattern)
            if await self.check_config_mode():
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
        output = await self.config_mode()
        logging.debug("Config commands are: {0}".format(config_commands))
        for cmd in config_commands:
            self._stdin.write(self.normalize_cmd(cmd))
            output += await self.read_until_prompt()

        if exit_config_mode:
            output += await self.exit_config_mode()

        logging.debug("Output is {0}".format(output))
        return output

    @staticmethod
    def strip_ansi_escape_codes(string_buffer):
        """
        Remove any ANSI (VT100) ESC codes from the output

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

        HP ProCurve's and F5 LTM's require this (possible others)
        """
        logging.info("In strip_ansi_escape_codes")
        logging.debug("repr = {0}".format(repr(string_buffer)))

        code_position_cursor = chr(27) + r'\[\d+;\d+H'
        code_show_cursor = chr(27) + r'\[\?25h'
        code_next_line = chr(27) + r'E'
        code_erase_line = chr(27) + r'\[2K'
        code_enable_scroll = chr(27) + r'\[\d+;\d+r'

        code_set = [code_position_cursor, code_show_cursor, code_erase_line, code_enable_scroll]

        output = string_buffer
        for ansi_esc_code in code_set:
            output = re.sub(ansi_esc_code, '', output)

        # CODE_NEXT_LINE must substitute with '\n'
        output = re.sub(code_next_line, '\n', output)

        logging.debug("new_output = %s" % output)
        logging.debug("repr = %s" % repr(output))

        return output

    def cleanup(self):
        """ Any needed cleanup before closing connection """
        self.exit_config_mode()
        self._stdin.write("exit\n")

    async def disconnect(self):
        """ Gracefully close the SSH connection """
        self.cleanup()
        self._conn.close()

    async def commit(self):
        """ Commit method for platforms that support this """
        raise AttributeError("Network device does not support 'commit()' method")
