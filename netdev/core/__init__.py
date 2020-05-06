"""
Copyright (c) 2019 Sergey Yakovlev <selfuryon@gmail.com>.

Core unit module
"""
from netdev.core.closures import enter_closure, enter_password_closure, exit_closure
from netdev.core.device_manager import DeviceManager
from netdev.core.device_stream import DeviceStream
from netdev.core.layer import Layer, LayerManager

__all__ = (
    "DeviceStream",
    "DeviceManager",
    "Layer",
    "LayerManager",
    "enter_closure",
    "enter_password_closure",
    "exit_closure",
)
