"""
Factory function for creating netdev classes
"""
from netdev.connections import SSHConnection, TelnetConnection
from netdev.core import (DeviceManager, DeviceStream, Layer, LayerManager,
                         enter_closure, exit_closure)
from netdev.vendors import (CiscoTerminalModes,
                                       create_cisco_like_dmanager)

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


def create_cisco_ios(conn):
    # Create device manager
    delimeter_list = [r">", r"#"]
    device_manager = create_cisco_like_dmanager(
        conn, delimeter_list, CiscoTerminalModes)
    return device_manager

# The keys of this dictionary are the supported device_types
CLASS_MAPPER = {
    "cisco_ios": create_cisco_ios,
}


platforms = list(CLASS_MAPPER.keys())
platforms.sort()
platforms_str = u"\n".join(platforms)

# handlers

def create(device_type:str, conn_type:str="ssh", **kwargs):
    """Factory function selects the proper class and creates object based on device_type"""
    conn = create_conn(conn_type,**kwargs)
    device_manager = CLASS_MAPPER[device_type](conn)
    return device_manager

