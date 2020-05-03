"""
Copyright (c) 2020 Sergey Yakovlev <selfuryon@gmail.com>.

This module provides Device Manager Class.
This class know how to work with device: know the right cli modes and how to writes to them.

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
    """ Device Manager for particular network device """

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
        self,
        cmd_list: List[str],
        target_cli_mode: IntEnum,
        return_cli_mode: IntEnum = None,
        timeout: int = None,
    ) -> str:
        """ 
        Go to specific cli mode and send the list of commands. 
        After that go to return_cli_mode if it isn't None 
        """
        cli_modes = self._layer_manager.cli_modes
        if isinstance(target_cli_mode, cli_modes) == False:
            target_cli_mode = cli_modes(target_cli_mode)
        if return_cli_mode:
            if isinstance(return_cli_mode, cli_modes) == False:
                return_cli_mode = cli_modes(return_cli_mode)
        self._logger.info(
            "Host %s: Send in %s cli mode list of commands: %s",
            self.host,
            target_cli_mode.name,
            cmd_list,
        )

        fut_return = None
        if return_cli_mode:
            fut_return = self._layer_manager.switch_to_layer(return_cli_mode)

        fut_target = self._layer_manager.switch_to_layer(target_cli_mode)
        fut_cmd = self._device_stream.send_commands(cmd_list)
        try:
            operation_timeout = timeout or self._timeout
            output = await asyncio.wait_for(fut_target, operation_timeout)
            output += await asyncio.wait_for(fut_cmd, operation_timeout)
            if fut_return:
                output += await asyncio.wait_for(fut_return, operation_timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(self.host)

        return output

    async def send_command(self, cmd_list: List[str], cli_mode: IntEnum = 1) -> str:
        """ Go to specific cli mode and send the list of commands """
        return await self.send_commands(cmd_list, cli_mode)

    async def send_config_set(self, cmd_list: List[str], cli_mode: IntEnum = 2) -> str:
        """ Go to specific cli mode and send the list of commands """
        return await self.send_commands(cmd_list, cli_mode, return_cli_mode=1)

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
