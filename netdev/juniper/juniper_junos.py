import re

from ..junos_like import JunOSLikeDevice
from ..logger import logger


class JuniperJunOS(JunOSLikeDevice):
    """Class for working with Juniper JunOS"""

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
        await self._check_shell_mode()
        await self._set_base_prompt()
        await self._disable_paging()
        logger.info("Host {}: Connected to device".format(self._host))

    async def _check_shell_mode(self):
        """Checking shell mode. If we are in shell - we automatically enter to cli"""
        logger.info("Host {}: checking shell mode".format(self._host))
        self._stdin.write(self._normalize_cmd("\n"))
        delimeter0 = self._get_default_command('delimeter0')
        delimeter1 = self._get_default_command('delimeter1')
        delimeter2 = self._get_default_command('delimeter2')
        prompt = await self._read_until_pattern(
            r"{}|{}|{}".format(re.escape(delimeter0), re.escape(delimeter1), re.escape(delimeter2)))
        prompt = prompt.strip()
        if self._ansi_escape_codes:
            prompt = self._strip_ansi_escape_codes(prompt)
        if not prompt:
            raise ValueError("Host {}: Unable to find prompt: {}".format(self._host, prompt))
        if '%' in prompt:
            logger.debug("Host {}: Entering to cli".format(self._host))
            self._stdin.write(self._normalize_cmd("cli"))

        return prompt
