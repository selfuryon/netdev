"""Subclass specific to Ubiquity Edge Switch"""
import re

from netdev.logger import logger
from netdev.vendors.devices.ios_like import IOSLikeDevice


class UbiquityEdgeSwitch(IOSLikeDevice):
    """Class for working with Ubiquity Edge Switches"""

    _pattern = r"\({prompt}.*?\) (\(.*?\))?[{delimiters}]"
    """Pattern for using in reading buffer. When it found processing ends"""

    _config_enter = "configure"
    """Command for entering to configuration mode"""

    async def _set_base_prompt(self):
        """
        Setting two important vars
            base_prompt - textual prompt in CLI (usually hostname)
            base_pattern - regexp for finding the end of command. IT's platform specific parameter

        For Ubiquity devices base_pattern is "(prompt) (\(.*?\))?[>|#]"
        """
        logger.info("Host {}: Setting base prompt".format(self.host))
        prompt = await self._find_prompt()
        # Strip off trailing terminator
        base_prompt = prompt[1:-3]
        self._conn.set_base_prompt(base_prompt)
        delimiters = map(re.escape, type(self)._delimiter_list)
        delimiters = r"|".join(delimiters)
        base_prompt = re.escape(base_prompt[:12])
        pattern = type(self)._pattern
        base_pattern = pattern.format(prompt=base_prompt, delimiters=delimiters)
        logger.debug("Host {}: Base Prompt: {}".format(self.host, base_prompt))
        logger.debug("Host {}: Base Pattern: {}".format(self.host, base_pattern))
        self._conn.set_base_pattern(base_pattern)
