from ..junos_like import JunOSLikeDevice
from ..logger import logger


class JuniperJunOS(JunOSLikeDevice):
    """Class for working with Juniper JunOS"""

    _shell_check = '%'
    _cli_command = 'cli'

    async def connect(self):
        """
        Juniper JunOS asynchronous connection method

        It connects to device and makes some preparation steps for working:

        * _establish_connection() for connecting to device
        * _check_shell_mode() for checking shell mode. If we are in shell - we automatically enter to cli
        * _set_base_prompt() for finding and setting device prompt
        * _disable_paging() for non interact output in commands
        """
        logger.info("Host {}: Connecting to device".format(self._host))
        await self._establish_connection()
        await self._set_base_prompt()
        await self._check_shell_mode()
        await self._disable_paging()
        logger.info("Host {}: Connected to device".format(self._host))

    async def _check_shell_mode(self):
        """Checking shell mode. If we are in shell - we automatically enter to cli"""
        logger.info("Host {}: Checking shell mode".format(self._host))
        output = ''
        prompt = await self._find_prompt()
        shell_check = type(self)._shell_check
        if shell_check in prompt:
            cli_command = type(self)._cli_command
            logger.debug("Host {}: Entering to cli".format(self._host))
            self._stdin.write(self._normalize_cmd(cli_command))
            output = await self._read_until_prompt()

        return output
