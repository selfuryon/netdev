"""
Copyright (c) 2019 Sergey Yakovlev <selfuryon@gmail.com>.

This module provides several classes for work with layers.

"""
import logging

from netdev.device_stream import DeviceStream
from netdev.logger import logger


class Layer:
    """Layer class fpr working with different terminal modes"""

    def __init__(
        self,
        name: str,
        device_stream: DeviceStream,
        enter_function,
        exit_function,
        transactional,
        commit_function,
    ):
        self._name = name
        self._device_stream = device_stream
        self._enter_function = enter_function
        self._exit_function = exit_function
        self._transactional = transactional
        self._commit_function = commit_function
        self._current_layer = None

    async def enter(self, cmd: str) -> None:
        """ Enter to this layer """
        self._enter_function(cmd)

    async def exit(self, cmd: str) -> None:
        """Exit from this layer"""
        self._exit_function(cmd)

    @property
    def _logger(self) -> logging.Logger:
        return logger.getChild("Layer")

    @property
    def name(self) -> str:
        """ Get the name of this layer """
        return self._name


class LayerManager:
    """ Layer Manager which manages terminal modes of network device """

    def __init__(self, device_stream: DeviceStream, checker_function):
        self._device_stream = device_stream
        self._checker_function = checker_function
        self._layers = {}

    def add_layer(self, layer: Layer):
        """ Add new layer with id started from 0 """
        id_layer = len(self._layers)
        self._layers[id_layer] = layer
        return self

    def switch_to_layer(self, layer_name: str) -> None:
        """ Switch to layer """

    def commmit_transaction(self, cmd: str) -> None:
        """ Commit the current transaction """


    @property
    def _logger(self) -> logging.Logger:
        return logger.getChild("LayerManager")
