from netdev.logger import logger
from netdev.vendors.terminal_modes.juniper import CliMode
from netdev.vendors.devices.junos_like import JunOSLikeDevice


class JuniperJunOS(JunOSLikeDevice):
    """Class for working with Juniper JunOS"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cli_mode = CliMode(
            enter_command=type(self)._cli_command,
            check_string=type(self)._cli_check,
            exit_command='',
            device=self
        )

    _cli_check = ">"
    """Checking string for shell mode"""

    _cli_command = "cli"
    """Command for entering to cli mode"""

    async def connect(self):
        """
        Juniper JunOS asynchronous connection method

        It connects to device and makes some preparation steps for working:

        * _establish_connection() for connecting to device
        * cli_mode() for checking shell mode. If we are in shell - we automatically enter to cli
        * _set_base_prompt() for finding and setting device prompt
        * _disable_paging() for non interact output in commands
        """
        logger.info("Host {}: Trying to connect to the device".format(self.host))
        await self._establish_connection()
        await self._session_preparation()
        await self._set_base_prompt()
        await self.cli_mode()
        await self._disable_paging()
        logger.info("Host {}: Entering to cmdline mode".format(self.host))
