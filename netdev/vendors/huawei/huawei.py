from netdev.vendors.comware_like import ComwareLikeDevice
import re
from netdev.logger import logger

class Huawei(ComwareLikeDevice):
    """Class for working with Huawei"""

    _disable_paging_command = "screen-length 0 temporary"
    """Command for disabling paging"""

    async def _set_base_prompt(self):
        """
        Setting two important vars
            base_prompt - textual prompt in CLI (usually hostname)
            base_pattern - regexp for finding the end of command. IT's platform specific parameter

        For Comware devices base_pattern is "[\]|>]prompt(\-\w+)?[\]|>]
        """
        logger.info("Host {}: Setting base prompt".format(self._host))
        prompt = await self._find_prompt()
        # Strip off any leading HRP_. characters for USGv5 HA
        prompt = re.sub(r"^HRP_.", "", prompt, flags=re.M)
        # Strip off trailing terminator
        self._base_prompt = prompt[1:-1]
        delimiter_right = map(re.escape, type(self)._delimiter_list)
        delimiter_right = r"|".join(delimiter_right)
        delimiter_left = map(re.escape, type(self)._delimiter_left_list)
        delimiter_left = r"|".join(delimiter_left)
        base_prompt = re.escape(self._base_prompt[:12])
        pattern = type(self)._pattern
        self._base_pattern = pattern.format(
            delimiter_left=delimiter_left,
            prompt=base_prompt,
            delimiter_right=delimiter_right,
        )
        logger.debug("Host {}: Base Prompt: {}".format(self._host, self._base_prompt))
        logger.debug("Host {}: Base Pattern: {}".format(self._host, self._base_pattern))
        return self._base_prompt