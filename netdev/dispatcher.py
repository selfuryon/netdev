"""
Factory function for creating netdev classes
"""
from netdev.vendors import AlcatelAOS
from netdev.vendors import AristaEOS
from netdev.vendors import ArubaAOS6, ArubaAOS8
from netdev.vendors import CiscoASA, CiscoIOS, CiscoIOSXR, CiscoNXOS, CiscoSG3XX
from netdev.vendors import FujitsuSwitch
from netdev.vendors import HPComware, HPComwareLimited
from netdev.vendors import JuniperJunOS
from netdev.vendors import MikrotikRouterOS
from netdev.vendors import Terminal
from netdev.vendors import UbiquityEdgeSwitch
from netdev.vendors import HW1000
from netdev.vendors import Huawei
from netdev.vendors import RuijieOS

# @formatter:off
# The keys of this dictionary are the supported device_types
CLASS_MAPPER = {
    "alcatel_aos": AlcatelAOS,
    "arista_eos": AristaEOS,
    "aruba_aos_6": ArubaAOS6,
    "aruba_aos_8": ArubaAOS8,
    "cisco_asa": CiscoASA,
    "cisco_ios": CiscoIOS,
    "cisco_ios_xe": CiscoIOS,
    "cisco_ios_xr": CiscoIOSXR,
    "cisco_nxos": CiscoNXOS,
    "cisco_sg3xx": CiscoSG3XX,
    "fujitsu_switch": FujitsuSwitch,
    "hp_comware": HPComware,
    "hp_comware_limited": HPComwareLimited,
    "juniper_junos": JuniperJunOS,
    "mikrotik_routeros": MikrotikRouterOS,
    "ubiquity_edge": UbiquityEdgeSwitch,
    "terminal": Terminal,
    "hw1000": HW1000,
    "huawei": Huawei,
    "ruijie_os": RuijieOS,
}

# @formatter:on

platforms = list(CLASS_MAPPER.keys())
platforms.sort()
platforms_str = u"\n".join(platforms)


def create(*args, **kwargs):
    """Factory function selects the proper class and creates object based on device_type"""
    if kwargs["device_type"] not in platforms:
        raise ValueError(
            "Unsupported device_type: "
            "currently supported platforms are: {0}".format(platforms_str)
        )
    connection_class = CLASS_MAPPER[kwargs["device_type"]]
    return connection_class(*args, **kwargs)
