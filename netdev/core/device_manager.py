"""
Copyright (c) 2019 Sergey Yakovlev <selfuryon@gmail.com>.

This module provides Device Manager Class

"""
import asyncio
import logging
from enum import IntEnum
from typing import List

from netdev.core.device_stream import DeviceStream
from netdev.core.layer import LayerManager
from netdev.exceptions import TimeoutError
from netdev.logger import logger


class DeviceManager:
    """ Device Manager Class """

    def __init__(
        self,
        device_stream: DeviceStream,
        layer_manager: LayerManager,
        timeout: int = 15,
    ):
        self._device_stream = device_stream
        self._layer_manager = layer_manager
        self._timeout = timeout

    async def send_commands(
        self, cmd_list: List[str], terminal_mode: IntEnum, timeout: int = None
    ) -> str:
        """ Go to specific terminal mode and send the list of commands """
        terminal_modes = self._layer_manager.terminal_modes
        if isinstance(terminal_mode, terminal_modes) == False:
            terminal_mode = terminal_modes(terminal_mode)
        self._logger.info(
            "Host %s: Send in %s terminal mode list of commands: %s",
            self.host,
            terminal_mode.name,
            cmd_list,
        )

        fut_switch = self._layer_manager.switch_to_layer(terminal_mode)
        fut_cmd = self._device_stream.send_commands(cmd_list)
        try:
            operation_timeout = timeout or self._timeout
            output = await asyncio.wait_for(fut_switch, operation_timeout)
            output += await asyncio.wait_for(fut_cmd, operation_timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(self.host)

        return output

    async def send_command(self, cmd_list: List[str], layer: IntEnum = 1) -> str:
        """ Go to specific layer and send the list of commands """
        return await self.send_commands(cmd_list, layer)

    async def send_config_set(self, cmd_list: List[str], layer: IntEnum = 2) -> str:
        """ Go to specific layer and send the list of commands """
        return await self.send_commands(cmd_list, layer)

    async def connect(self) -> None:
        """ Establish connection """
        await self._device_stream.connect()

    async def disconnect(self) -> None:
        """ Close connection """
        await self._device_stream.disconnect()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

    @property
    def host(self) -> str:
        """ Return the host address """
        return self._device_stream.host

    @property
    def _logger(self) -> logging.Logger:
        return logger.getChild("DeviceManager")
