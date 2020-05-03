"""
Copyright (c) 2019 Sergey Yakovlev <selfuryon@gmail.com>.

This module provides several classes for work with layers.

"""
import logging
from enum import IntEnum
from typing import Callable

from netdev.core.device_stream import DeviceStream
from netdev.logger import logger


class Layer:
    """Layer class for working with different cli modes"""

    def __init__(
        self,
        cli_mode: IntEnum,
        device_stream: DeviceStream,
        enter_func: Callable[[DeviceStream], str],
        exit_func: Callable[[DeviceStream], str],
        transactional: bool = False,
        commit_func: Callable[[DeviceStream], str] = None,
    ) -> None:
        self._cli_mode = cli_mode
        self._device_stream = device_stream
        self._transactional = transactional

        self._enter_func = enter_func
        self._exit_func = exit_func
        self._commit_func = commit_func

    async def enter(self) -> str:
        """ Enter to this cli mode"""
        self._logger.info("Layer %s: Enter to this cli mode", self._cli_mode.name)

        output = await self._enter_func(self._device_stream)  # type: str
        self._logger.debug(
            "Layer %s: Output after entering to this cli mode: %s",
            self._cli_mode.name,
            output,
        )
        return output

    async def exit(self) -> str:
        """Exit from this cli mode"""
        self._logger.info("Layer %s: Exit from cli mode", self._cli_mode.name)

        output = ""  # type: str
        if self._transactional:
            output = await self.commit()
        output += await self._exit_func(self._device_stream)
        self._logger.debug(
            "Layer %s: Output after exiting from layer: %s",
            self._cli_mode.name,
            output,
        )
        return output

    async def commit(self) -> str:
        """ Commit changes for this layer if layer is transactional """

        if self._transactional:
            self._logger.info("Layer %s: Commit the changes", self._cli_mode.name)

            output = await self._commit_func(self._device_stream)  # type: str
            self._logger.debug(
                "Layer %s: Output after commiting the changes: %s",
                self._cli_mode.name,
                output,
            )
            return output

        self._logger.info("Layer %s: Commiting is not supported", self._cli_mode.name)

    @property
    def transactional(self):
        """ If layer is transactional you need to commit changes """
        return self._transactional

    @property
    def cli_mode(self) -> str:
        """ Get the terminal cli_mode for this layer """
        return self._cli_mode

    @property
    def _logger(self) -> logging.Logger:
        return logger.getChild("LayerManager.Layer")


class LayerManager:
    """ Layer Manager which manages terminal cli_modes of network device """

    def __init__(
        self,
        device_stream: DeviceStream,
        cli_modes: IntEnum,
        check_func: Callable[[str], str],
    ):
        self._device_stream = device_stream
        self._check_func = check_func
        self._cli_modes = cli_modes
        self._layers = {}
        self._current_cli_mode = None

    def add_layer(self, layer: Layer):
        """ Add new layer with order from less privilage to more privilage"""
        self._layers[layer.cli_mode.value] = layer
        return self

    async def switch_to_layer(self, target_cli_mode: IntEnum) -> str:
        """ Switch to layer """
        current_cli_mode = await self.current_cli_mode()

        if current_cli_mode == target_cli_mode:
            self._logger.info(
                "LayerManager: Don't need to switch to different terminal cli_mode"
            )
            return ""

        self._logger.info(
            "LayerManager: Switching from %s to %s terminal cli_mode",
            current_cli_mode,
            target_cli_mode,
        )

        output = ""  # type:str
        if current_cli_mode < target_cli_mode:
            while current_cli_mode != target_cli_mode:
                layer = self._layers[current_cli_mode + 1]
                current_cli_mode = layer.cli_mode
                output += await layer.enter()

        elif current_cli_mode > target_cli_mode:
            while current_cli_mode != target_cli_mode:
                layer = self._layers[current_cli_mode - 1]
                current_cli_mode = layer.cli_mode
                output += await layer.exit()

        self._current_cli_mode = current_cli_mode
        return output

    async def current_cli_mode(self) -> IntEnum:
        """ Get current terminal cli_mode. If it's unknown we run the checker function to get that """
        if self._current_cli_mode is None:
            buf = await self._device_stream.send_commands("\n", strip_prompt=False)
            self._current_cli_mode = await self._check_func(buf)
        self._logger.info("Current cli_mode is %s", self._current_cli_mode)
        return self._current_cli_mode

    @property
    def cli_modes(self) -> IntEnum:
        return self._cli_modes

    @property
    def _logger(self) -> logging.Logger:
        return logger.getChild("LayerManager")
