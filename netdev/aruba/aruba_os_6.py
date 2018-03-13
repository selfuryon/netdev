"""Subclass specific to Aruba AOS 6.x"""

from ..ios_like import IOSLikeDevice
from ..logger import logger


class ArubaAOS6(IOSLikeDevice):
    """Class for working with Aruba OS 6.X"""

    _disable_paging_command = 'no paging'
    """Command for disabling paging"""

    _config_exit = 'exit'
    """Command for existing from configuration mode to privilege exec"""

    _config_check = ') (config'
    """Checking string in prompt. If it's exist im prompt - we are in configuration mode"""

    _pattern = r"\({}.*?\) (\(.*?\))?\s?[{}]"
    """Pattern for using in reading buffer. When it found processing ends"""

    async def exit_config_mode(self):
        """Exit from configuration mode"""
        logger.info('Host {}: Exiting from configuration mode'.format(self._host))
        output = ''
        exit_config = type(self)._config_exit
        # Considering max 3 level of submode in config mode
        for i in range(3):
            if await self.check_config_mode():
                self._stdin.write(self._normalize_cmd(exit_config))
                output += await self._read_until_prompt()
            else:
                return output

        if await self.check_config_mode():
            raise ValueError("Failed to exit from configuration mode")

        return output
