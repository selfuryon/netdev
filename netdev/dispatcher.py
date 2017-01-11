"""
Factory function for creating netdev classes
"""
from .arista import AristaEOS
from .cisco import CiscoASA
from .cisco import CiscoIOS
from .cisco import CiscoNXOS
from .fujitsu import FujitsuSwitch
from .hp import HPComware
from .hp import HPComwareLimited
from .juniper import JuniperJunOS
from .mikrotik import MikrotikRouterOS

# @formatter:off
# The keys of this dictionary are the supported device_types
CLASS_MAPPER = {
    'cisco_ios': CiscoIOS,
    'cisco_xe': CiscoIOS,
    'cisco_asa': CiscoASA,
    'cisco_nxos': CiscoNXOS,
    'hp_comware': HPComware,
    'hp_comware_limited': HPComwareLimited,
    'fujitsu_switch': FujitsuSwitch,
    'mikrotik_routeros': MikrotikRouterOS,
    'arista_eos': AristaEOS,
    'juniper_junos': JuniperJunOS,
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
