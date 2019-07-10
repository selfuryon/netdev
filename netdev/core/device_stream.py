"""
Copyright (c) 2019 Sergey Yakovlev <selfuryon@gmail.com>.

This module provides device stream class.
Device Stream is the basic abstraction upon different IO Connections.
Device Stream can send a list of commands to device and it understand
the device prompt, so it can read the buffer till the end of output

"""
import logging
import re
from typing import List

from netdev.connections import IOConnection
from netdev.logger import logger


class DeviceStream:
    """ Class which know how to work with the device in a stream mode """

    def __init__(self, io_connection: IOConnection, prompt_pattern: str = r"") -> None:
        if io_connection:
            self._io_connection = io_connection
        else:
            raise ValueError("IO Connection must be set")
        self._prompt_pattern = prompt_pattern

    async def send(self, cmd_list: List[str]) -> None:
        """ Send list of commands to stream """
        self._logger.debug(
            "Host %s: Send to stream list of commands: %r", self.host, cmd_list
        )
        if isinstance(cmd_list, str):
            cmd_list = [cmd_list]

        for cmd in cmd_list:
            cmd = self._normalize_cmd(cmd)
            self._io_connection.send(cmd)

    async def read_until(self, patterns: str, re_flags, until_prompt=True) -> None:
        """ Read the output from stream until patterns or/and prompt """
        if patterns is None and not until_prompt:
            raise ValueError("Pattern can't be None with until_prompt=False")

        pattern_list = []

        if isinstance(patterns, str):
            pattern_list.append(patterns)
        elif isinstance(patterns, list):
            pattern_list += patterns

        if until_prompt:
            pattern_list.append(self._prompt_pattern)

        output = ""
        self._logger.debug("Host %s: Read until patterns: %r", self.host, pattern_list)
        while True:
            tmp = await self._io_connection.read()
            self._logger.debug("Host %s: Read from buffer: %r", self.host, tmp)
            output += tmp

            for regexp in pattern_list:
                if re.search(regexp, output, flags=re_flags):
                    self._logger.debug(
                        "Host %s: find pattern [%r] in buffer: %s",
                        self.host,
                        regexp,
                        output,
                    )
                    return output

    @property
    def _logger(self) -> logging.Logger:
        return logger.getChild("DeviceStream")

    @property
    def host(self) -> str:
        """ Return the host address """
        return self._io_connection.host

    @staticmethod
    def _normalize_cmd(cmd: str) -> str:
        """Normalize CLI commands to have a single trailing newline"""
        cmd = cmd.rstrip("\n") + "\n"
        return cmd
