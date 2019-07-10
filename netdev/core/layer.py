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
    """Layer class fpr working with different terminal modes"""

    def __init__(
        self,
        name: str,
        device_stream: DeviceStream,
        enter_func: Callable[[DeviceStream], str],
        exit_func: Callable[[DeviceStream], str],
        transactional: bool = False,
        commit_func: Callable[[DeviceStream], str] = None,
    ) -> None:
        self._name = name
        self._device_stream = device_stream
        self._transactional = transactional

        self._enter_func = enter_func
        self._exit_func = exit_func
        self._commit_func = commit_func

    async def enter(self) -> str:
        """ Enter to this layer """
        self._logger.info("Layer %s: Enter to layer", self._name)

        output = self._enter_func(self._device_stream)  # type: str
        self._logger.debug(
            "Layer %s: Output after entering to layer: %s", self._name, output
        )
        return output

    async def exit(self) -> str:
        """Exit from this layer"""
        self._logger.info("Layer %s: Exit from layer", self._name)

        output = ""  # type: str
        if self._transactional:
            output = await self.commit()
        output += self._exit_func(self._device_stream)
        self._logger.debug(
            "Layer %s: Output after exiting from layer: %s", self._name, output
        )
        return output

    async def commit(self) -> str:
        """ Commit changes for this layer if layer is transactional """

        if self._transactional:
            self._logger.info("Layer %s: Commit the changes", self._name)

            output = self._commit_func(self._device_stream)  # type: str
            self._logger.debug(
                "Layer %s: Output after commiting the changes: %s", self._name, output
            )
            return output

        self._logger.info("Layer %s: Commiting is not supported", self._name)

    @property
    def transactional(self):
        """ If layer is transactional you need to commit changes """
        return self._transactional

    @property
    def name(self) -> str:
        """ Get the name of this layer """
        return self._name

    @property
    def _logger(self) -> logging.Logger:
        return logger.getChild("Layer")


class LayerManager:
    """ Layer Manager which manages terminal modes of network device """

    def __init__(
        self,
        device_stream: DeviceStream,
        layers_enum: IntEnum,
        checker_func: Callable[[DeviceStream], str],
    ):
        self._device_stream = device_stream
        self._checker_func = checker_func
        self._layers_enum = layers_enum
        self._layers = {}
        self._current_layer = None

    def add_layer(self, layer_id: IntEnum, layer: Layer):
        """ Add new layer with order from less privilage to more privilage"""
        self._logger.debug("LayerManager: Add new layer with ID:%s", layer_id)

        self._layers[layer_id] = layer
        return self

    async def switch_to_layer(self, layer_id: IntEnum) -> str:
        """ Switch to layer """
        current_layer = self._current_layer or self.current_layer()

        if layer_id == current_layer:
            self._logger.debug("LayerManager: Don't need to swith to different layer")
            return ""

        self._logger.debug(
            "LayerManager: Switching from %s to %s layer", current_layer, layer_id
        )

        output = ""  # type:str
        if layer_id > current_layer:
            for num in range(current_layer, layer_id):
                layer_id = self._layers_enum(num)
                layer = self._layers[layer_id]
                output = await layer.enter()

        elif layer_id < current_layer:
            for num in range(current_layer, layer_id):
                layer_id = self._layers_enum(num)
                layer = self._layers[layer_id]
                output = await layer.exit()

        return output

    def current_layer(self) -> IntEnum:
        """ Get current layer. If it's unknown we run the checker funtion to get that """
        if self._current_layer is None:
            self._current_layer = self._checker_func(self._device_stream)
        return self._current_layer

    @property
    def _logger(self) -> logging.Logger:
        return logger.getChild("LayerManager")
