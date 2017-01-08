import re

from ..ios_like import IOSLikeDevice
from ..logger import logger


class FujitsuSwitch(IOSLikeDevice):
    """Class for working with Fujitsu Blade switch"""

    _pattern = r"\({}.*?\) (\(.*?\))?[{}]"
    _disable_paging_command = 'no pager'
    _config_enter = 'conf'

    async def _set_base_prompt(self):
        """
        Setting two important vars
            base_prompt - textual prompt in CLI (usually hostname)
            base_pattern - regexp for finding the end of command. IT's platform specific parameter

        For Fujitsu devices base_pattern is "(prompt) (\(.*?\))?[>|#]"
        """
        logger.info("Host {}: Setting base prompt".format(self._host))
        prompt = await self._find_prompt()
        # Strip off trailing terminator
        self._base_prompt = prompt[1:-3]
        delimiters = r"|".join(type(self)._delimiter_list)
        pattern = type(self)._pattern
        self._base_pattern = pattern.format(self._base_prompt[:12], delimiters)
        logger.debug("Host {}: Base Prompt: {}".format(self._host, self._base_prompt))
        logger.debug("Host {}: Base Pattern: {}".format(self._host, self._base_pattern))
        return self._base_prompt

    @staticmethod
    def _normalize_linefeeds(a_string):
        """
        Convert '\r\r\n','\r\n', '\n\r' to '\n and remove extra '\n\n' in the text
        """
        newline = re.compile(r'(\r\r\n|\r\n|\n\r)')
        return newline.sub('\n', a_string).replace('\n\n', '\n')
