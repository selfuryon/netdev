from netdev.vendors.arista import AristaEOS
from netdev.vendors.aruba import ArubaAOS8, ArubaAOS6
from netdev.vendors.base import BaseDevice
from netdev.vendors.cisco import CiscoNXOS, CiscoIOSXR, CiscoASA, CiscoIOS
from netdev.vendors.comware_like import ComwareLikeDevice
from netdev.vendors.fujitsu import FujitsuSwitch
from netdev.vendors.hp import HPComware, HPComwareLimited
from netdev.vendors.ios_like import IOSLikeDevice
from netdev.vendors.juniper import JuniperJunOS
from netdev.vendors.junos_like import JunOSLikeDevice
from netdev.vendors.mikrotik import MikrotikRouterOS
from netdev.vendors.terminal import Terminal
from netdev.vendors.ubiquiti import UbiquityEdgeSwitch

__all__ = (
    "CiscoASA",
    "CiscoIOS",
    "CiscoIOSXR",
    "CiscoNXOS",
    "HPComware",
    "HPComwareLimited",
    "FujitsuSwitch",
    "MikrotikRouterOS",
    "JuniperJunOS",
    "JunOSLikeDevice",
    "AristaEOS",
    "ArubaAOS6",
    "ArubaAOS8",
    "BaseDevice",
    "IOSLikeDevice",
    "ComwareLikeDevice",
    "Terminal",
    "arista",
    "aruba",
    "cisco",
    "fujitsu",
    "hp",
    "juniper",
    "mikrotik",
    "UbiquityEdgeSwitch",
)
