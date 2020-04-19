"""
Copyright (c) 2019 Sergey Yakovlev <selfuryon@gmail.com>.

This module provides different closures for working with cisco-like devices

"""
from enum import IntEnum
from re import match
from typing import List

from netdev.core import DeviceStream


class CiscoTerminalMode(IntEnum):
    """ Configuration modes for Cisco-Like devices """

    unprivilege_exec = 0
    privilege_exec = 1
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


def cisco_check_closure(unprivilege_pattern, privilege_pattern, config_pattern):
    """ Generates cisco_like checker """

    async def cisco_checker(prompt: str) -> IntEnum:
        result = None  # type: CiscoTerminalMode
        if config_pattern in prompt:
            result = CiscoTerminalMode.config_mode
        elif privilege_pattern in prompt:
            result = CiscoTerminalMode.privilege_exec
        elif unprivilege_pattern in prompt:
            result = CiscoTerminalMode.unprivilege_exec
        else:
            raise ValueError("Can't find the terminal mode")

        return result

    return cisco_checker


def cisco_set_prompt_closure(delimeter_list: List[str]):
    """ Generates cisco-like set_prompt function """

    def cisco_set_prompt(buf: str) -> str:
        delimeters = r"|".join(delimeter_list)
        delimeters = rf"[{delimeters}]"
        config_mode = r"(\(.*?\))?"
        buf = buf.strip().split('\n')[-1]
        pattern = rf"($i([\s\d-_]+)\s?[{delimeters}])"
        prompt = match(pattern, buf).group(1)
        prompt_pattern = prompt + config_mode + delimeters
        return prompt_pattern

    return cisco_set_prompt
