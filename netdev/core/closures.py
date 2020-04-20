"""
Copyright (c) 2019 Sergey Yakovlev <selfuryon@gmail.com>.

This module provides basic closures for DeviceManager and LayerManager

"""

from netdev.core.device_stream import DeviceStream


def enter_closure(enter_cmd: str):
    """ Generates cisco-like enter function """

    async def enter(device_stream: DeviceStream) -> str:
        output = await device_stream.send_commands(enter_cmd)
        return output

    return enter


def exit_closure(exit_cmd: str):
    """ Generates cisco-like exit function """

    async def exit(device_stream: DeviceStream) -> str:
        output = await device_stream.send_commands(exit_cmd)
        return output

    return exit
