"""
Factory function for creating netdev classes
"""
from typing import Callable

from netdev.connections import SSHConnection, TelnetConnection
from netdev.core import (DeviceManager, DeviceStream, Layer, LayerManager,
                         enter_closure, exit_closure)
from netdev.vendors import CiscoCLIModes, cisco_device_manager


def create_conn(conn_type, **kwargs):
    # Create connection
    conn = None
    if conn_type == "ssh":
        conn = SSHConnection(**kwargs)
    elif conn_type == "telnet":
        conn = TelnetConnection(**kwargs)
    else:
        raise ValueError("Non-supported connection type")
    return conn


def cisco_ios(conn, secret):
    # Create device manager for Cisco IOS
    delimeter_list = [r">", r"#"]
    check_pattern_list = [r">", r"#", r")#"]
    nopage_cmd = "term len 0"
    device_manager = cisco_device_manager(
        conn, CiscoCLIModes, delimeter_list, check_pattern_list, nopage_cmd, secret
    )
    return device_manager


# The keys of this dictionary are the supported device_types
CLASS_MAPPER = {
    "cisco_ios": cisco_ios,
}


platforms = list(CLASS_MAPPER.keys())
platforms.sort()
platforms_str = "\n".join(platforms)

# handlers


def create(device_type: str, conn_type: str = "ssh", secret: str = "", **kwargs):
    """Factory function selects the proper class and creates object based on device_type"""
    conn = create_conn(conn_type, **kwargs)
    device_manager = CLASS_MAPPER[device_type](conn, secret)
    return device_manager
