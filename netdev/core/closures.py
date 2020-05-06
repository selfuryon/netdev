"""
Copyright (c) 2020 Sergey Yakovlev <selfuryon@gmail.com>.

This module provides basic closures for DeviceManager and LayerManager

"""

import re

from netdev.core.device_stream import DeviceStream


def enter_closure(enter_cmd: str):
    """ Generates enter function """

    async def enter(device_stream: DeviceStream) -> str:
        output = await device_stream.send_commands(enter_cmd, strip_command=False, strip_prompt=False)
        return output

    return enter


def enter_password_closure(enter_cmd: str, password: str, pattern: str = r"password"):
    """ Generates enter function when you also need to type a password """

    async def enter(device_stream: DeviceStream) -> str:
        output = await device_stream.send_commands(
            enter_cmd, strip_command=False, strip_prompt=False, patterns=[pattern], re_flags=re.IGNORECASE,
        )
        if re.search(pattern, output, flags=re.IGNORECASE):
            output += await device_stream.send_commands(password)
        return output

    return enter


def exit_closure(exit_cmd: str):
    """ Generates exit function """

    async def exit(device_stream: DeviceStream) -> str:
        output = await device_stream.send_commands(exit_cmd, strip_command=False, strip_prompt=False)
        return output

    return exit
