from netdev.vendors.base import BaseDevice
from netdev.logger import logger
import asyncio
import re

class AlcatelAOS(BaseDevice):
    """Class for working with Alcatel AOS"""


    async def _read_until_prompt_or_pattern(self, pattern="", re_flags=0):
        """Read until either self.base_pattern or pattern is detected. Return ALL data available"""
        output = ""
        logger.info("Host {}: Reading until prompt or pattern".format(self._host))
        if not pattern:
            pattern = self._base_pattern
        base_prompt_pattern = self._base_pattern
        while True:
            fut = self._stdout.read(self._MAX_BUFFER)
            try:
                output += await asyncio.wait_for(fut, self._timeout)
                #print("123:")
                #print(output)
                #print("*" * 80)
            except asyncio.TimeoutError:
                raise TimeoutError(self._host)
            if re.search("\n" + pattern, output, flags=re_flags) or re.search(
                "\n" + base_prompt_pattern, output, flags=re_flags
            ):
            
            #if re.search("\nrprd-opcinet091 - ADMIN ==> ", output, flags=re_flags):
            
                logger.debug(
                    "Host {}: Reading pattern '{}' or '{}' was found: {}".format(
                        self._host, pattern, base_prompt_pattern, repr(output)
                    )
                )
                return output

