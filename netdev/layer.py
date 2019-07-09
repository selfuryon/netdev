"""
Copyright (c) 2019 Sergey Yakovlev <selfuryon@gmail.com>.

This module provides several classes for work with layers.

"""
import logging
from typing import Awaitable

from netdev.device_stream import DeviceStream
from netdev.logger import logger


class Layer:
    """Layer class fpr working with different terminal modes"""

    def __init__(
        self,
        name: str,
        device_stream: DeviceStream,
        enter_func,
        exit_func,
        transactional: bool = False,
        commit_func=None,
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

    async def commit(self,) -> str:
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

    def __init__(self, device_stream: DeviceStream, checker_function):
        self._device_stream = device_stream
        self._checker_function = checker_function
        self._layers_id = {}
        self._layers_name = {}
        self._current_layer = None

    def add_layer(self, layer: Layer):
        """ Add new layer with order from less privilage to more privilage"""
        layer_id = len(self._layers_id)
        self._layers_id[layer_id] = layer
        self._layers_name[layer.name] = layer
        return self

    def switch_to_layer(self, layer_name: str) -> None:
        """ Switch to layer """

    def commmit_transaction(self, cmd: str) -> None:
        """ Commit the current transaction """

    @property
    def _logger(self) -> logging.Logger:
        return logger.getChild("LayerManager")
