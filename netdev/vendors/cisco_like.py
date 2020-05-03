"""
Copyright (c) 2019 Sergey Yakovlev <selfuryon@gmail.com>.

This module provides different closures for working with cisco-like devices

"""
import re
from enum import IntEnum
from typing import Callable, List

from netdev.connections import IOConnection
from netdev.core import (DeviceManager, DeviceStream, Layer, LayerManager,
                         enter_closure, exit_closure)


class CiscoModes(IntEnum):
    """ Configuration modes for Cisco-Like devices """

    UNPRIVILEGE_EXEC = 0
    PRIVILEGE_EXEC = 1
    CONFIG = 2


def cisco_check_closure(unprivilege_pattern, privilege_pattern, config_pattern):
    """ Generates cisco_like checker """

    async def cisco_checker(prompt: str) -> IntEnum:
        result = None  # type: CiscoTerminalMode
        if config_pattern in prompt:
            result = CiscoModes.CONFIG
        elif privilege_pattern in prompt:
            result = CiscoModes.PRIVILEGE_EXEC
        elif unprivilege_pattern in prompt:
            result = CiscoModes.UNPRIVILEGE_EXEC
        else:
            raise ValueError("Can't find the terminal mode")

        return result

    return cisco_checker


def cisco_set_prompt_closure(delimeter_list: List[str]):
    """ Generates cisco-like set_prompt function """

    def cisco_set_prompt(buf: str) -> str:
        escaped_list = map(re.escape, delimeter_list)
        delimeters = r"|".join(escaped_list)
        delimeters = rf"[{delimeters}]"
        config_mode = r"(\(.*?\))?"
        buf = buf.strip().split("\n")[-1]
        pattern = rf"([\w\d\-\_]+)\s?{delimeters}"
        prompt = re.match(pattern, buf).group(1)
        prompt_pattern = prompt + config_mode + delimeters
        return prompt_pattern

    return cisco_set_prompt


def create_cisco_like_dmanager(
    conn: IOConnection,
    delimeter_list: List[str],
    terminal_modes: IntEnum,
    # check_func: Callable[[str], str],
):
    # Create Cisco Like Device Manager
    set_prompt_func = cisco_set_prompt_closure(delimeter_list)
    dstream = DeviceStream(conn, delimeter_list, set_prompt_func, "term len 0")
    # Create Layers
    unprivilege_layer = Layer(
        terminal_modes(0),
        dstream,
        enter_func=None,
        exit_func=None,
        transactional=False,
        commit_func=None,
    )
    privilege_layer = Layer(
        terminal_modes(1),
        dstream,
        enter_func=enter_closure("enable"),
        exit_func=exit_closure("exit"),
        transactional=False,
        commit_func=None,
    )
    config_layer = Layer(
        terminal_modes(2),
        dstream,
        enter_func=enter_closure("conf t"),
        exit_func=exit_closure("exit"),
        transactional=False,
        commit_func=None,
    )
    # Create Layer Manager
    layer_manager = LayerManager(
        dstream, terminal_modes, cisco_check_closure(r">", r"#", r")#")
    )
    layer_manager.add_layer(unprivilege_layer)
    layer_manager.add_layer(privilege_layer)
    layer_manager.add_layer(config_layer)
    # Create Device Manager
    device_manager = DeviceManager(dstream, layer_manager)
    return device_manager
