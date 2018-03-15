"""
Factory function for creating netdev classes
"""
from .vendors import AristaEOS
from .vendors import ArubaAOS6
from .vendors import ArubaAOS8
from .vendors import CiscoASA
from .vendors import CiscoIOS
from .vendors import CiscoIOSXR
from .vendors import CiscoNXOS
from .vendors import FujitsuSwitch
from .vendors import HPComware
from .vendors import HPComwareLimited
from .vendors import JuniperJunOS
from .vendors import MikrotikRouterOS

# @formatter:off
# The keys of this dictionary are the supported device_types
CLASS_MAPPER = {
    'cisco_ios': CiscoIOS,
    'cisco_ios_xe': CiscoIOS,
    'cisco_ios_xr': CiscoIOSXR,
    'cisco_asa': CiscoASA,
    'cisco_nxos': CiscoNXOS,
    'hp_comware': HPComware,
    'hp_comware_limited': HPComwareLimited,
    'fujitsu_switch': FujitsuSwitch,
    'mikrotik_routeros': MikrotikRouterOS,
    'arista_eos': AristaEOS,
    'juniper_junos': JuniperJunOS,
    'aruba_aos_6': ArubaAOS6,
    'aruba_aos_8': ArubaAOS8,
}

# @formatter:on

platforms = list(CLASS_MAPPER.keys())
platforms.sort()
platforms_str = u"\n".join(platforms)


def create(*args, **kwargs):
    """Factory function selects the proper class and creates object based on device_type"""
    if kwargs['device_type'] not in platforms:
        raise ValueError('Unsupported device_type: '
                         'currently supported platforms are: {0}'.format(platforms_str))
    connection_class = CLASS_MAPPER[kwargs['device_type']]
    return connection_class(*args, **kwargs)
