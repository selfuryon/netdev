from netdev.logger import logger
from netdev.vendors.devices.base import BaseDevice


class MikrotikRouterOS(BaseDevice):
    """Class for working with Mikrotik RouterOS"""

    def __init__(self, *args, **kwargs):
        """
        Initialize class for asynchronous working with network devices
        Invoke init with some special params (base_pattern and username)

        :param str host: device hostname or ip address for connection
        :param str username: username for logging to device
        :param str password: user password for logging to device
        :param int port: ssh port for connection. Default is 22
        :param str device_type: network device type
        :param known_hosts: file with known hosts. Default is None (no policy). With () it will use default file
        :param str local_addr: local address for binding source of tcp connection
        :param client_keys: path for client keys. Default in None. With () it will use default file in OS
        :param str passphrase: password for encrypted client keys
        :param float timeout: timeout in second for getting information from channel
        :param loop: asyncio loop object

        Mikrotik duplicate prompt in connection, so we should use pattern like
        prompt .* prompt.
        For disabling colors in CLI output we should user this username = username+c
        '+c' disables colors
        '+t' disable auto term capabilities detection
        '+200w' set terminal width to 200 rows
        """
        super().__init__(*args, **kwargs)
        self._base_pattern = r"\[.*?\] \>.*\[.*?\] \>"
        self._username += "+ct200w"
        self._ansi_escape_codes = True

    _pattern = r"\[.*?\] (\/.*?)?\>"

    async def _flush_buffer(self):
        await self._conn._read_until_prompt()

    async def _set_base_prompt(self):
        """
        Setting two important vars
        * base_prompt - textual prompt in CLI (usually hostname)
        * base_pattern - regexp for finding the end of command. IT's platform specific parameter

        For Mikrotik devices base_pattern is "r"\[.*?\] (\/.*?)?\>"
        """
        self._logger.info("Host {}: Setting base prompt".format(self.host))
        self._base_pattern = type(self)._pattern
        prompt = await self._find_prompt()
        user = ""
        # Strip off trailing terminator
        prompt = prompt[1:-3]
        if "@" in prompt:
            prompt = prompt.split("@")[1]
        self._base_prompt = prompt
        self._logger.debug("Host {}: Base Prompt: {}".format(self.host, self._base_prompt))
        self._logger.debug("Host {}: Base Pattern: {}".format(self.host, self._base_pattern))
        return self._base_prompt

    async def _find_prompt(self):
        """Finds the current network device prompt, last line only."""
        self._logger.info("Host {}: Finding prompt".format(self.host))
        prompt = await self._send_command_expect("\r")
        prompt = prompt.strip()
        if self._ansi_escape_codes:
            prompt = self._strip_ansi_escape_codes(prompt)
        if not prompt:
            raise ValueError("Unable to find prompt: {0}".format(prompt))
        self._logger.debug("Host {}: Prompt: {}".format(self.host, prompt))
        return prompt

    @staticmethod
    def _normalize_cmd(command):
        """Specific trailing newline for Mikrotik"""
        command = command.rstrip("\n")
        command += "\r"
        return command
