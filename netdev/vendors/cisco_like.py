"""
Copyright (c) 2019 Sergey Yakovlev <selfuryon@gmail.com>.

This module provides different closures for working with cisco-like devices

"""
from enum import IntEnum

from netdev.core import DeviceStream


class CiscoTerminalMode(IntEnum):
    """ Configuration modes for Cisco-Like devices """

    unprivilage_exec = 0
    privilage_exec = 1
    config_mode = 2


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


def cisco_checker_closure(unprivilege_pattern, privilege_pattern, config_pattern):
    """ Generates cisco_like checker """

    async def cisco_checker(prompt: str) -> IntEnum:
        result = None  # type: CiscoTerminalMode
        if config_pattern in prompt:
            result = CiscoTerminalMode.config_mode
        elif privilege_pattern in prompt:
            result = CiscoTerminalMode.privilage_exec
        elif unprivilege_pattern in prompt:
            result = CiscoTerminalMode.unprivilage_exec
        else:
            raise ValueError("Can't find the terminal mode")

        return result

    return cisco_checker
