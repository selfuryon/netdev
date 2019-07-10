"""
Copyright (c) 2019 Sergey Yakovlev <selfuryon@gmail.com>.

This module provides Device Manager Class

"""
import logging
import asyncio
from typing import List
from enum import IntEnum

from netdev.exceptions import TimeoutError
from netdev.device_stream import DeviceStream
from netdev.layer import LayerManager
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
        self, cmd_list: List[str], layer: IntEnum, timeout: int = None
    ) -> str:
        """ Go to specific layer and send the list of commands """
        self._logger.info(
            "Host %s: Send in layer %s list of commands: %s", self.host, layer, cmd_list
        )

        fut_switch = self._layer_manager.switch_to_layer(layer)
        fut_cmd = self._device_stream.send(cmd_list)
        try:
            operation_timeout = timeout or self._timeout
            output = await asyncio.wait_for(fut_switch, operation_timeout)  # type: str
            output += await asyncio.wait_for(fut_cmd, operation_timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(self.host)

        return output

    async def send_command(self, cmd_list: List[str], layer: IntEnum) -> str:
        """ Go to specific layer and send the list of commands """
        return await self.send_commands(cmd_list, layer)

    async def send_config_set(self, cmd_list: List[str], layer: IntEnum) -> str:
        """ Go to specific layer and send the list of commands """
        return await self.send_commands(cmd_list, layer)

    @property
    def host(self) -> str:
        """ Return the host address """
        return self._device_stream.host

    @property
    def _logger(self) -> logging.Logger:
        return logger.getChild("DeviceManager")
