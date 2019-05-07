from netdev.logger import logger
from netdev.vendors.junos_like import JunOSLikeDevice


class JuniperJunOS(JunOSLikeDevice):
    """Class for working with Juniper JunOS"""

    _cli_check = '>'
    """Checking string for shell mode"""

    _cli_command = 'cli'
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
        logger.info("Host {}: Trying to connect to the device".format(self._host))
        await self._establish_connection()
        await self._set_base_prompt()
        await self.cli_mode()
        await self._disable_paging()
        logger.info("Host {}: Entering to cmdline mode".format(self._host))

    async def check_cli_mode(self):
        """Check if we are in cli mode. Return boolean"""
        logger.info('Host {}: Checking shell mode'.format(self._host))
        cli_check = type(self)._cli_check
        self._stdin.write(self._normalize_cmd('\n'))
        output = await self._read_until_prompt()
        return cli_check in output

    async def cli_mode(self):
        """Enter to cli mode"""
        logger.info("Host {}: Entering to cli mode".format(self._host))
        output = ""
        cli_command = type(self)._cli_command
        if not await self.check_cli_mode():
            self._stdin.write(self._normalize_cmd(cli_command))
            output += await self._read_until_prompt()
            if not await self.check_cli_mode():
                raise ValueError("Failed to enter to cli mode")
        return output
