"""
Copyright (c) 2019 Sergey Yakovlev <selfuryon@gmail.com>.

This module provides device stream class.
Device Stream is the basic abstraction upon different IO Connections.
Device Stream can send a list of commands to device and it understand
the device prompt, so it can read the buffer till the end of output

"""
import logging
import re
from typing import Callable, List

from netdev.connections import IOConnection
from netdev.logger import logger


class DeviceStream:
    """ Class which know how to work with the device in a stream mode """

    def __init__(
            self, io_connection: IOConnection, delimeter_list: [str], set_prompt_func: Callable[[str], str] = None, nopage_cmd: str = None
    ) -> None:
        if io_connection:
            self._io_connection = io_connection
        else:
            raise ValueError("IO Connection must be set")
        if set_prompt_func:
            self._set_prompt_func = set_prompt_func
        else:
            raise ValueError("Need to set prompt setter closure")
        self._prompt_pattern = r"|".join(
            delimeter_list)  # First time promt pattern
        self._nopage_cmd = nopage_cmd

    async def disconnect(self) -> None:
        """ Close connection """
        await self._io_connection.disconnect()

    async def connect(self) -> None:
        """ Establish connection """
        await self._io_connection.connect()
        # Trying to detect right prompt by 2 attempts
        await self.send_commands("\n")
        buf = await self.send_commands("\n", strip_prompt=False)
        self._prompt_pattern = self._set_prompt_func(buf)
        await self.send_commands(self._nopage_cmd)
        self._logger.debug(
            "Host %s: Set prompt pattern to: %s", self.host, self._prompt_pattern
        )

    async def send_commands(
        self,
        cmd_list: List[str],
        *,
        strip_command: bool = True,
        strip_prompt: bool = True,
        patterns: List[str] = None,
        re_flags=0,
    ):
        """ Send list of commands to stream """
        self._logger.debug(
            "Host %s: Send to stream list of commands: %r", self.host, cmd_list
        )

        pattern_list = []  # type: list[str]
        if not patterns:
            pattern_list = [self._prompt_pattern]
        elif isinstance(patterns, str):
            pattern_list = [patterns, self._prompt_pattern]
        elif isinstance(patterns, list):
            pattern_list = patterns + [self._prompt_pattern]
        else:
            raise ValueError("Patterns can be set only to str or List[str]")

        if isinstance(cmd_list, str):
            cmd_list = [cmd_list]

        output = ""
        for cmd in cmd_list:
            await self._send(cmd)
            buf = await self._read_until(pattern_list, re_flags)
            buf = self._strip_command(cmd, buf) if strip_command else buf
            buf = self._strip_prompt(buf) if strip_prompt else buf
            output += buf

        return output

    async def _send(self, cmd: str) -> None:
        """ Send command to stream """
        cmd = self._normalize_cmd(cmd)
        await self._io_connection.send(cmd)

    async def _read_until(self, patterns: List[str], re_flags) -> str:
        """ Read the output from stream until patterns """
        if patterns is None:
            raise ValueError("Pattern can't be None")

        output = ""
        self._logger.debug(
            "Host %s: Read until patterns: %r", self.host, patterns)
        while True:
            buf = await self._io_connection.read()
            self._logger.debug("Host %s: Read from buffer: %r", self.host, buf)
            output += buf

            for regexp in patterns:
                if re.search(regexp, output, flags=re_flags):
                    self._logger.debug(
                        "Host %s: find pattern [%r] in buffer: %r",
                        self.host,
                        regexp,
                        output,
                    )
                    output = self._normalize_linefeeds(output)
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

    @staticmethod
    def _strip_prompt(output: str) -> str:
        """ Strip the trailing router prompt from the output """
        output_lines = output.split("\n")
        new_output = "\n".join(output_lines[:-1])
        return new_output

    @staticmethod
    def _strip_command(cmd: str, output: str) -> str:
        """
        Strip command_string from output string
        Cisco IOS adds backspaces into output for long commands
        """
        backspace_char = "\x08"
        new_output = ""

        if backspace_char in output:
            output = output.replace(backspace_char, "")
            output_lines = output.split("\n")
            new_output = "\n".join(output_lines[1:])
        else:
            command_length = len(cmd)
            new_output = output[command_length:]

        return new_output

    @staticmethod
    def _normalize_linefeeds(output: str) -> str:
        """Convert '\r\r\n','\r\n', '\n\r' to '\n"""
        newline = re.compile(r"(\r\r\n|\r\n|\n\r)")
        return newline.sub("\n", output)
