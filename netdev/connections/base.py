import re
import asyncio
from netdev.logger import logger
from .interface import IConnection


class BaseConnection(IConnection):

    def __init__(self, *args, **kwargs):
        self._host = None
        self._timeout = None
        self._transport = self._conn = None
        self._base_prompt = self._base_pattern = ""
        self._MAX_BUFFER = 65535
        self._ansi_escape_codes = False
        self._base_pattern = ''
        self._base_prompt = ''

    async def __aenter__(self):
        """Async Context Manager"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async Context Manager"""
        await self.disconnect()

    def set_base_prompt(self, prompt):
        self._base_prompt = prompt

    def set_base_pattern(self, pattern):
        self._base_pattern = pattern

    def disconnect(self):
        """ Close Connection """
        raise NotImplementedError("Connection must implement disconnect method")

    def connect(self):
        """ Establish Connection """
        raise NotImplementedError("Connection must implement connect method")

    def send(self, cmd):
        """ send Command """
        raise NotImplementedError("Connection must implement send method")

    async def read(self):
        raise NotImplementedError("Connection must implement read method ")

    async def read_until_pattern(self, pattern, re_flags=0):
        """Read channel until pattern detected. Return ALL data available"""

        if pattern is None:
            raise ValueError("pattern cannot be None")

        if isinstance(pattern, str):
            pattern = [pattern]
        output = ""
        logger.info("Host {}: Reading until pattern".format(self._host))

        logger.debug("Host {}: Reading pattern: {}".format(self._host, pattern))
        while True:
            fut = self.read()
            try:
                output += await asyncio.wait_for(fut, self._timeout)
            except asyncio.TimeoutError:
                raise TimeoutError(self._host)

            for exp in pattern:
                if re.search(exp, output, flags=re_flags):
                    logger.debug(
                        "Host {}: Reading pattern '{}' was found: {}".format(
                            self._host, pattern, repr(output)
                        )
                    )
                    return output

    async def read_until_prompt(self):
        """ read util prompt """
        return await self.read_until_pattern(self._base_pattern)

    async def read_until_prompt_or_pattern(self, pattern, re_flags=0):
        """ read util prompt or pattern """

        logger.info("Host {}: Reading until prompt or pattern".format(self._host))

        if isinstance(pattern, str):
            pattern = [self._base_prompt, pattern]
        elif isinstance(pattern, list):
            pattern = [self._base_prompt] + pattern
        else:
            raise ValueError("pattern must be string or list of strings")
        return await self.read_until_pattern(pattern=pattern, re_flags=re_flags)
