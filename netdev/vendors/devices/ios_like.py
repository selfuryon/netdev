"""
IOSLikeDevice Class is abstract class for using in Cisco IOS like devices

Connection Method are based upon AsyncSSH and should be running in asyncio loop
"""
import re
from netdev.logger import logger
from netdev.vendors.devices.base import BaseDevice
from netdev.vendors.terminal_modes.cisco import EnableMode, ConfigMode


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

        self.current_terminal = None

        self.enable_mode = EnableMode(
            enter_command=type(self)._priv_enter,
            exit_command=type(self)._priv_exit,
            check_string=type(self)._priv_check,
            device=self
        )
        self.config_mode = ConfigMode(
            enter_command=type(self)._config_enter,
            exit_command=type(self)._config_exit,
            check_string=type(self)._config_check,
            device=self,
            parent=self.enable_mode
        )

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



    async def _session_preparation(self):
        await super()._session_preparation()
        await self.enable_mode()
        await self._disable_paging()

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
            output += await self.config_mode.exit()

        output = self._normalize_linefeeds(output)
        logger.debug(
            "Host {}: Config commands output: {}".format(self.host, repr(output))
        )
        return output

    async def _cleanup(self):
        """ Any needed cleanup before closing connection """
        logger.info("Host {}: Cleanup session".format(self.host))
        await self.config_mode.exit()
