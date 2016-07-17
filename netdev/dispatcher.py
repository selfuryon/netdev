"""
Factory function for creating netdev classes
"""
from netdev.cisco import CiscoAsa
from netdev.cisco import CiscoIos
from netdev.cisco import CiscoNxos
from netdev.hp import HPComware
from netdev.fujitsu import FujitsuSwitch
from netdev.mikrotik import MikrotikRouterOS

# @formatter:off
# The keys of this dictionary are the supported device_types
CLASS_MAPPER = {
    'cisco_ios': CiscoIos,
    'cisco_xe': CiscoIos,
    'cisco_asa': CiscoAsa,
    'cisco_nxos': CiscoNxos,
    'hp_comware': HPComware,
    'fujitsu_switch': FujitsuSwitch,
    'mikrotik_routeros': MikrotikRouterOS,
}

# @formatter:on

platforms = list(CLASS_MAPPER.keys())
platforms.sort()
platforms_str = u"\n".join(platforms)


def connect(*args, **kwargs):
    """Factory function selects the proper class and creates object based on device_type"""
    if kwargs['device_type'] not in platforms:
        raise ValueError('Unsupported device_type: '
                         'currently supported platforms are: {0}'.format(platforms_str))
    connection_class = CLASS_MAPPER[kwargs['device_type']]
    return connection_class(*args, **kwargs)
