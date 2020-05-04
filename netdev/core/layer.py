"""
Copyright (c) 2020 Sergey Yakovlev <selfuryon@gmail.com>.

This module provides several classes for work with layers.
Each Layer represent the CLI mode and methods for enter and exit to this CLI mode
LayerManager is special class which know how to switch between layers (CLI modes)

"""
import logging
from enum import IntEnum
from typing import Callable

from netdev.core.device_stream import DeviceStream
from netdev.exceptions import SwitchError
from netdev.logger import logger


class Layer:
    """Layer class for working with particular cli mode"""

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
        self._logger.info(
            "Host %s: %s cli mode: Enter to this cli mode",
            self.host,
            self._cli_mode.name,
        )

        output = await self._enter_func(self._device_stream)  # type: str
        self._logger.debug(
            "Host %s: %s cli mode: Output after entering to this cli mode: %s",
            self.host,
            self._cli_mode.name,
            output,
        )
        return output

    async def exit(self) -> str:
        """ Exit from this cli mode """
        self._logger.info(
            "Host %s: %s cli mode: Exit from this cli mode",
            self.host,
            self._cli_mode.name,
        )

        output = ""  # type: str
        if self._transactional:
            output = await self.commit()
        output += await self._exit_func(self._device_stream)
        self._logger.debug(
            "Host %s: %s cli mode: Output after exiting from this cli mode: %s",
            self.host,
            self._cli_mode.name,
            output,
        )
        return output

    async def commit(self) -> str:
        """ Commit changes for this cli mode if layer is transactional """

        if self._transactional:
            self._logger.info(
                "Host %s: %s cli mode: Commit changes", self.host, self._cli_mode.name
            )

            output = await self._commit_func(self._device_stream)  # type: str
            self._logger.debug(
                "Host %s: %s cli mode: Output after commiting changes: %s",
                self.host,
                self._cli_mode.name,
                output,
            )
            return output

        self._logger.info(
            "Host %s: %s cli mode: Commiting is not supported",
            self.host,
            self._cli_mode.name,
        )

    @property
    def transactional(self):
        """ If layer is transactional you need to commit changes """
        return self._transactional

    @property
    def cli_mode(self) -> str:
        """ Get the cli mode for this layer """
        return self._cli_mode

    @property
    def host(self) -> str:
        """ Get the cli mode for this layer """
        return self._device_stream.host

    @property
    def _logger(self) -> logging.Logger:
        return logger.getChild("LayerManager.Layer")


class LayerManager:
    """ Layer Manager manages cli modes of network device """

    def __init__(
        self,
        device_stream: DeviceStream,
        cli_modes: IntEnum,
        check_func: Callable[[str], str] = None,
    ):
        self._device_stream = device_stream
        self._check_func = check_func
        self._cli_modes = cli_modes
        self._layers = {}
        self._current_cli_mode = None

    def add_layer(self, layer: Layer):
        """ Add new layer for managing """
        self._layers[layer.cli_mode.value] = layer
        return self

    async def switch_to_layer(self, target_cli_mode: IntEnum) -> str:
        """ Switch to target cli mode """
        current_cli_mode = await self.current_cli_mode()

        if current_cli_mode == target_cli_mode:
            self._logger.info(
                "Host %s: Don't need to switch to different cli mode", self.host
            )
            return ""

        self._logger.info(
            "Host %s: Switching from %s to %s cli mode",
            self.host,
            current_cli_mode.name,
            target_cli_mode.name,
        )

        output = ""  # type:str
        if current_cli_mode < target_cli_mode:
            while current_cli_mode != target_cli_mode:
                layer = self._layers[current_cli_mode + 1]
                output += await layer.enter()
                current_cli_mode = layer.cli_mode
                real_cli_mode = await self.check_cli_mode()
                if current_cli_mode != real_cli_mode:
                    raise SwitchError(self.host, f"Cannot enter to {current_cli_mode}")

        elif current_cli_mode > target_cli_mode:
            while current_cli_mode != target_cli_mode:
                layer = self._layers[current_cli_mode - 1]
                output += await layer.exit()
                current_cli_mode = layer.cli_mode
                real_cli_mode = await self.check_cli_mode()
                if current_cli_mode != real_cli_mode:
                    raise SwitchError(self.host, f"Cannot exit from {current_cli_mode}")

        self._current_cli_mode = current_cli_mode
        return output

    async def check_cli_mode(self) -> IntEnum:
        """ Check current cli mode """
        self._logger.info("Host %s: Recognizing the current cli mode", self.host)
        buf = await self._device_stream.send_commands("\n", strip_prompt=False)
        current_cli_mode = await self._check_func(buf)
        self._logger.info(
            "Host %s: Recognized cli mode is %s", self.host, current_cli_mode.name
        )
        return current_cli_mode

    async def current_cli_mode(self) -> IntEnum:
        """ Get current cli mode """
        self._current_cli_mode = self._current_cli_mode or await self.check_cli_mode()
        self._logger.info(
            "Host %s: Current cli mode is %s", self.host, self._current_cli_mode.name
        )
        return self._current_cli_mode

    @property
    def cli_modes(self) -> IntEnum:
        return self._cli_modes

    @property
    def host(self) -> IntEnum:
        return self._device_stream.host

    @property
    def _logger(self) -> logging.Logger:
        return logger.getChild("LayerManager")
