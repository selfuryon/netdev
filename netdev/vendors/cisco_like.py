"""
Copyright (c) 2019 Sergey Yakovlev <selfuryon@gmail.com>.

This module provides different closures for working with cisco-like devices

"""
from netdev.core import DeviceStream


def cisco_enter_closure(enter_cmd: str):
    """ Generates cisco-like enter function """

    async def cisco_enter(device_stream: DeviceStream) -> str:
        output = await device_stream.send_commands(enter_cmd)
        return output

    return cisco_enter


def cisco_exit_closure(exit_cmd: str):
    """ Generates cisco-like exit function """

    async def cisco_exit(device_stream: DeviceStream) -> str:
        output = await device_stream.send_commands(exit_cmd)
        return output

    return cisco_exit
