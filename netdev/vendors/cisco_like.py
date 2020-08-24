"""
Copyright (c) 2019 Sergey Yakovlev <selfuryon@gmail.com>.

This module provides different closures for working with cisco-like devices

"""
import re
from enum import IntEnum
from typing import Callable, List

from netdev.connections import IOConnection
from netdev.core import (DeviceManager, DeviceStream, Layer, LayerManager,
                         enter_closure, enter_password_closure, exit_closure)


class CiscoCLIModes(IntEnum):
    """ Configuration modes for Cisco-Like devices """

    UNPRIVILEGE_EXEC = 0
    PRIVILEGE_EXEC = 1
    CONFIG = 2


def cisco_check_closure(unprivilege_pattern, privilege_pattern, config_pattern):
    """ Generate cisco_like checker for current cli mode """

    async def cisco_checker(prompt: str) -> IntEnum:
        """ Check current cli mode """
        result = None  # type: CiscoTerminalMode
        if config_pattern in prompt:
            result = CiscoCLIModes.CONFIG
        elif privilege_pattern in prompt:
            result = CiscoCLIModes.PRIVILEGE_EXEC
        elif unprivilege_pattern in prompt:
            result = CiscoCLIModes.UNPRIVILEGE_EXEC
        else:
            raise ValueError("Can't find the cli mode")

        return result

    return cisco_checker


def cisco_set_prompt_closure(delimeter_list: List[str]):
    """ Generate cisco-like set_prompt function """

    def cisco_set_prompt(buf: str) -> str:
        """ Prompt setter for cisco like devices """
        escaped_list = map(re.escape, delimeter_list)
        delimeters = r"|".join(escaped_list)
        delimeters = rf"[{delimeters}]"
        config_mode = r"(\(.*?\))?"
        buf = buf.strip().split("\n")[-1]
        pattern = rf"([\w\d\-\_]+)\s?{delimeters}"
        prompt = re.match(pattern, buf)
        if not prompt:
            raise Exception("Cannot set the prompt")
        prompt = prompt.group(1)
        prompt_pattern = prompt + config_mode + delimeters
        return prompt_pattern

    return cisco_set_prompt


def cisco_device_manager(
    conn: IOConnection,
    cli_modes: IntEnum,
    delimeter_list: List[str],
    check_pattern_list: List[str],
    nopage_cmd: str,
    secret: str = "",
):
    # Create Cisco Like Device Manager
    set_prompt_func = cisco_set_prompt_closure(delimeter_list)
    dstream = DeviceStream(conn, delimeter_list, set_prompt_func, nopage_cmd)

    # Create Layers
    unprivilege_layer = Layer(
        cli_modes(0), dstream, enter_func=None, exit_func=None, transactional=False, commit_func=None,
    )
    privilege_layer = Layer(
        cli_modes(1),
        dstream,
        enter_func=enter_password_closure("enable", secret),
        exit_func=exit_closure("exit"),
        transactional=False,
        commit_func=None,
    )
    config_layer = Layer(
        cli_modes(2),
        dstream,
        enter_func=enter_closure("conf t"),
        exit_func=exit_closure("exit"),
        transactional=False,
        commit_func=None,
    )
    # Create Layer Manager
    layer_manager = LayerManager(dstream, cli_modes, cisco_check_closure(*check_pattern_list))
    layer_manager.add_layer(unprivilege_layer)
    layer_manager.add_layer(privilege_layer)
    layer_manager.add_layer(config_layer)
    # Create Device Manager
    device_manager = DeviceManager(dstream, layer_manager)
    return device_manager


def ciscoxr_device_manager(
    conn: IOConnection,
    cli_modes: IntEnum,
    delimeter_list: List[str],
    check_pattern_list: List[str],
    nopage_cmd: str,
    secret: str = "",
):
    # Create Cisco Like Device Manager
    set_prompt_func = cisco_set_prompt_closure(delimeter_list)
    dstream = DeviceStream(conn, delimeter_list, set_prompt_func, nopage_cmd)

    # Create Layers
    unprivilege_layer = Layer(
        cli_modes(0), dstream, enter_func=None, exit_func=None, transactional=False, commit_func=None,
    )
    privilege_layer = Layer(
        cli_modes(1),
        dstream,
        enter_func=enter_password_closure("enable", secret),
        exit_func=exit_closure("exit"),
        transactional=False,
        commit_func=None,
    )
    config_layer = Layer(
        cli_modes(2),
        dstream,
        enter_func=enter_closure("conf t"),
        exit_func=exit_closure("exit"),
        transactional=False,
        commit_func=None,
    )
    # Create Layer Manager
    layer_manager = LayerManager(dstream, cli_modes, cisco_check_closure(*check_pattern_list))
    layer_manager.add_layer(unprivilege_layer)
    layer_manager.add_layer(privilege_layer)
    layer_manager.add_layer(config_layer)
    # Create Device Manager
    device_manager = DeviceManager(dstream, layer_manager)
    return device_manager
