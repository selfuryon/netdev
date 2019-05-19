from netdev.vendors.devices.arista import AristaEOS
from netdev.vendors.devices.aruba import ArubaAOS8, ArubaAOS6
from netdev.vendors.devices.base import BaseDevice
from netdev.vendors.devices.cisco import CiscoNXOS, CiscoIOSXR, CiscoASA, CiscoIOS
from netdev.vendors.devices.comware_like import ComwareLikeDevice
from netdev.vendors.devices.fujitsu import FujitsuSwitch
from netdev.vendors.devices.hp import HPComware, HPComwareLimited
from netdev.vendors.devices.ios_like import IOSLikeDevice
from netdev.vendors.devices.juniper import JuniperJunOS
from netdev.vendors.devices.junos_like import JunOSLikeDevice
from netdev.vendors.devices.mikrotik import MikrotikRouterOS
from netdev.vendors.devices.terminal import Terminal
from netdev.vendors.devices.ubiquiti import UbiquityEdgeSwitch

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
