"""
IOSLikeDevice Class is abstract class for using in Cisco IOS like devices

Connection Method are based upon AsyncSSH and should be running in asyncio loop
"""

import re

from netdev.logger import logger
from netdev.vendors.base import BaseDevice


class IOSLikeDevice(BaseDevice):
    """
    This Class is abstract class for working with Cisco IOS like devices

    Cisco IOS like devices having several concepts:

    * user exec or unprivileged exec. This mode allows you perform basic tests and get system information.
    * privilege exec. This mode allows the use of all EXEC mode commands available on the system
    * configuration mode or config mode. This mode are used for configuration whole system.
    """

    def __init__(self, secret=u"", *args, **kwargs):
        """
        Initialize class for asynchronous working with network devices

        :param str host: device hostname or ip address for connection
        :param str username: username for logging to device
        :param str password: user password for logging to device
        :param str secret: secret password for privilege mode
        :param int port: ssh port for connection. Default is 22
        :param str device_type: network device type
        :param known_hosts: file with known hosts. Default is None (no policy). With () it will use default file
        :param str local_addr: local address for binding source of tcp connection
        :param client_keys: path for client keys. Default in None. With () it will use default file in OS
        :param str passphrase: password for encrypted client keys
        :param float timeout: timeout in second for getting information from channel
        :param loop: asyncio loop object
        """
        super().__init__(*args, **kwargs)
        self._secret = secret

    _priv_enter = "enable"
    """Command for entering to privilege exec"""

    _priv_exit = "disable"
    """Command for existing from privilege exec to user exec"""

    _priv_check = "#"
    """Checking string in prompt. If it's exist im prompt - we are in privilege exec"""

    _config_enter = "conf t"
    """Command for entering to configuration mode"""

    _config_exit = "end"
    """Command for existing from configuration mode to privilege exec"""

    _config_check = ")#"
    """Checking string in prompt. If it's exist im prompt - we are in configuration mode"""

    async def connect(self):
        """
        Basic asynchronous connection method for Cisco IOS like devices

        It connects to device and makes some preparation steps for working.
        Usual using 4 functions:

        * _establish_connection() for connecting to device
        * _set_base_prompt() for finding and setting device prompt
        * _enable() for getting privilege exec mode
        * _disable_paging() for non interact output in commands
        """
        logger.info("Host {}: Trying to connect to the device".format(self._host))
        await self._establish_connection()
        await self._set_base_prompt()
        await self.enable_mode()
        await self._disable_paging()
        logger.info("Host {}: Has connected to the device".format(self._host))

    async def check_enable_mode(self):
        """Check if we are in privilege exec. Return boolean"""
        logger.info("Host {}: Checking privilege exec".format(self._host))
        check_string = type(self)._priv_check
        self._stdin.write(self._normalize_cmd("\n"))
        output = await self._read_until_prompt()
        return check_string in output

    async def enable_mode(self, pattern="password", re_flags=re.IGNORECASE):
        """Enter to privilege exec"""
        logger.info("Host {}: Entering to privilege exec".format(self._host))
        output = ""
        enable_command = type(self)._priv_enter
        if not await self.check_enable_mode():
            self._stdin.write(self._normalize_cmd(enable_command))
            output += await self._read_until_prompt_or_pattern(
                pattern=pattern, re_flags=re_flags
            )
            if re.search(pattern, output, re_flags):
                self._stdin.write(self._normalize_cmd(self._secret))
                output += await self._read_until_prompt()
            if not await self.check_enable_mode():
                raise ValueError("Failed to enter to privilege exec")
        return output

    async def exit_enable_mode(self):
        """Exit from privilege exec"""
        logger.info("Host {}: Exiting from privilege exec".format(self._host))
        output = ""
        exit_enable = type(self)._priv_exit
        if await self.check_enable_mode():
            self._stdin.write(self._normalize_cmd(exit_enable))
            output += await self._read_until_prompt()
            if await self.check_enable_mode():
                raise ValueError("Failed to exit from privilege exec")
        return output

    async def check_config_mode(self):
        """Checks if the device is in configuration mode or not"""
        logger.info("Host {}: Checking configuration mode".format(self._host))
        check_string = type(self)._config_check
        self._stdin.write(self._normalize_cmd("\n"))
        output = await self._read_until_prompt()
        return check_string in output

    async def config_mode(self):
        """Enter into config_mode"""
        logger.info("Host {}: Entering to configuration mode".format(self._host))
        output = ""
        config_command = type(self)._config_enter
        if not await self.check_config_mode():
            self._stdin.write(self._normalize_cmd(config_command))
            output = await self._read_until_prompt()
            if not await self.check_config_mode():
                raise ValueError("Failed to enter to configuration mode")
        return output

    async def exit_config_mode(self):
        """Exit from configuration mode"""
        logger.info("Host {}: Exiting from configuration mode".format(self._host))
        output = ""
        exit_config = type(self)._config_exit
        if await self.check_config_mode():
            self._stdin.write(self._normalize_cmd(exit_config))
            output = await self._read_until_prompt()
            if await self.check_config_mode():
                raise ValueError("Failed to exit from configuration mode")
        return output

    async def send_config_set(self, config_commands=None, exit_config_mode=True):
        """
        Sending configuration commands to Cisco IOS like devices
        Automatically exits/enters configuration mode.

        :param list config_commands: iterable string list with commands for applying to network devices in conf mode
        :param bool exit_config_mode: If true it will quit from configuration mode automatically
        :return: The output of this commands
        """

        if config_commands is None:
            return ""

        # Send config commands
        output = await self.config_mode()
        output += await super().send_config_set(config_commands=config_commands)

        if exit_config_mode:
            output += await self.exit_config_mode()

        output = self._normalize_linefeeds(output)
        logger.debug(
            "Host {}: Config commands output: {}".format(self._host, repr(output))
        )
        return output

    async def _cleanup(self):
        """ Any needed cleanup before closing connection """
        logger.info("Host {}: Cleanup session".format(self._host))
        await self.exit_config_mode()
