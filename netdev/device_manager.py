"""
Copyright (c) 2019 Sergey Yakovlev <selfuryon@gmail.com>.

This module provides Device Manager Class

"""
import logging
from typing import List

from netdev.device_stream import DeviceStream
from netdev.layer import LayerManager
from netdev.logger import logger


class DeviceManager:
    """ Device Manager Class """

    def __init__(self, device_stream: DeviceStream, layer_manager: LayerManager):
        self._device_stream = device_stream
        self._layer_manager = layer_manager

    async def send_commands(self, cmd_list: List[str], layer: str) -> str:
        """ Go to specific layer and send the list of commands """
        output = ""
        output = await self._layer_manager.switch_to_layer(layer)
        output += await self._device_stream.send(cmd_list)
        return output

    async def send_command(self, cmd_list: List[str], layer: str) -> str:
        """ Go to specific layer and send the list of commands """
        return await self.send_commands(cmd_list, layer)

    async def send_config_set(self, cmd_list: List[str], layer: str) -> str:
        """ Go to specific layer and send the list of commands """
        return await self.send_commands(cmd_list, layer)

    @property
    def _logger(self) -> logging.Logger:
        return logger.getChild("DeviceManager")
