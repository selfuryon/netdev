import logging

import asyncssh

from netdev.netdev_base import NetDevSSH


class MikrotikRouterOSSSH(NetDevSSH):
    def __init__(self, ip=u'', host=u'', username=u'', password=u'', secret=u'', port=22, device_type=u'',
                 ssh_strict=False):
        """
        Invoke init with some special params (base_pattern and username)

        Mikrotik duplicate prompt in connection, so we should use pattern like
        prompt .* prompt.
        For disabling colors in CLI output we should user this username = username+c
        '+c' disables colors
        '+t' disable auto term capabilities detection
        '+80w' set terminal width to 80 rows
        """
        super(MikrotikRouterOSSSH, self).__init__(ip=ip, host=host, username=username, password=password, secret=secret,
                                                  port=port, device_type=device_type, ssh_strict=ssh_strict)

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
        await self._establish_connection()
        await self._set_base_prompt()

    @property
    def _priv_prompt_term(self):
        return '>'

    @property
    def _unpriv_prompt_term(self):
        return self._priv_prompt_term

    async def _establish_connection(self):
        """
        Need change the read until prompt not pattern with priv or unpriv terminators
        """
        output = ""
        # initiate SSH connection
        self._conn = await asyncssh.connect(**self._connect_params_dict)
        self._stdin, self._stdout, self._stderr = await self._conn.open_session(term_type='dumb')
        # Flush unnecessary data
        output = await self._read_until_prompt()
        logging.info("Start Connection to {0}:{1}".format(self._host, self._port))
        logging.debug("Establish Connection Output: {0}".format(output))
        return output

    async def _set_base_prompt(self):
        """
        Setting two important vars
            base_prompt - textual prompt in CLI (usually hostname)
            base_pattern - regexp for finding the end of command. IT's platform specific parameter

        For Mikrotik devices base_pattern is "<
        """
        self._base_pattern = r"\[.*?\] (\/.*?)?\>"
        logging.info("In set_base_prompt")
        self._stdin.write("\r")
        prompt = await self._find_prompt()
        user = ''
        # Strip off trailing terminator
        prompt = prompt.splitlines()
        prompt = prompt[-1][1:-4]
        if '@' in prompt:
            prompt = prompt.split('@')[1]
        self.base_prompt = prompt
        logging.debug("Base Prompt is {0}".format(self.base_prompt))
        logging.debug("Base Pattern is {0}".format(self._base_pattern))
        return self.base_prompt

    async def _find_prompt(self):
        """Finds the current network device prompt, last line only."""
        logging.info("In find_prompt")
        self._stdin.write("\r")
        prompt = ''
        prompt = await self._read_until_prompt()
        prompt = prompt.strip()
        if self._ansi_escape_codes:
            prompt = self._strip_ansi_escape_codes(prompt)
        if not prompt:
            raise ValueError("Unable to find prompt: {0}".format(prompt))
        logging.debug("Prompt is {0}".format(prompt))
        return prompt

    async def _config_mode(self, config_command='config', exit_config_mode=True):
        """No need for entering configuration mode"""
        return ""

    async def _exit_config_mode(self, exit_config='end', pattern=''):
        """No need for exiting configuration mode"""
        return ""

    async def send_command(self, command_string, strip_command=True, strip_prompt=False):
        return await super(MikrotikRouterOSSSH, self).send_command(command_string, strip_command, strip_prompt)

    @staticmethod
    def _normalize_cmd(command):
        """Specific trailing newline for Mikrotik"""
        command = command.rstrip("\n")
        command += '\r'
        return command
