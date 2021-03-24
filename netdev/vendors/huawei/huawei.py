from netdev.vendors.comware_like import ComwareLikeDevice
import re
import asyncio
import asyncssh
from netdev.exceptions import TimeoutError, DisconnectError
from netdev.logger import logger

class Huawei(ComwareLikeDevice):
    """Class for working with Huawei"""
    # system view or commit时会多出~，*
    _delimiter_left_list = ["<", "[","[*","[~"]

    _disable_paging_command = "screen-length 0 temporary"
    """Command for disabling paging"""

    async def _establish_connection(self):
        """Establishing SSH connection to the network device"""
        logger.info(
            "Host {}: Establishing connection to port {}".format(self._host, self._port)
        )
        output = ""
        # initiate SSH connection
        fut = asyncssh.connect(**self._connect_params_dict)
        try:
            self._conn = await asyncio.wait_for(fut, self._timeout)
        except asyncssh.DisconnectError as e:
            raise DisconnectError(self._host, e.code, e.reason)
        except asyncio.TimeoutError:
            raise TimeoutError(self._host)
        self._stdin, self._stdout, self._stderr = await self._conn.open_session(
            term_type="Dumb", term_size=(200, 24)
        )
        logger.info("Host {}: Connection is established".format(self._host))
        # Flush unnecessary data
        delimiters = map(re.escape, type(self)._delimiter_list)
        delimiters = r"|".join(delimiters)
        output = await self._read_until_pattern(delimiters)
        logger.debug(
            "Host {}: Establish Connection Output: {}".format(self._host, repr(output))
        )
        # When asked change password, choose N
        if "The password needs to be changed. Change now? [Y/N]:" in output:
            self._stdin.write(self._normalize_cmd("N\n"))
            output = await self._read_until_pattern(delimiters)
        return output

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
    