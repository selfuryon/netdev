"""
Copyright (c) 2019 Sergey Yakovlev <selfuryon@gmail.com>.

This module provides device stream class.
Device Stream is the basic abstraction upon different IO Connections.

"""
from netdev.logger import logger


class DeviceStream:
    """ Class which know how to work with the device in a stream mode """

    def __init__(self, io_connection, prompt_pattern=r""):
        self._io_connection = io_connection
        self._prompt_pattern = prompt_pattern

    async def send(self, cmd_list):
        """ Send list of commands to stream """
        self._logger.debug(
            "Host %s: Send to stream list of commands: %r", self.host, cmd_list
        )
        if isinstance(cmd_list, str):
            cmd_list = [cmd_list]

        for cmd in cmd_list:
            cmd = self._normalize_cmd(cmd)
            self._io_connection.send(cmd)

    async def read_until(self, pattern, re_flags, until_prompt=True):
        """ Read the output from stream """
        if pattern is None and not until_prompt:
            raise ValueError("Pattern can't be None with until_prompt=False")

    @property
    def _logger(self):
        return logger.getChild("DeviceStream")

    @property
    def host(self):
        """ Return the host address """
        return self.io_connection.host

    @staticmethod
    def _normalize_cmd(cmd):
        """Normalize CLI commands to have a single trailing newline"""
        cmd = cmd.rstrip("\n") + "\n"
        return cmd
