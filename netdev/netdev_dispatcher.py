"""
Factory function for creating netdev
"""
from netdev.cisco import CiscoAsaSSH
from netdev.cisco import CiscoIosSSH
from netdev.cisco import CiscoNxosSSH
from netdev.hp import HPComwareSSH

# The keys of this dictionary are the supported device_types
CLASS_MAPPER = {'cisco_ios': CiscoIosSSH, 'cisco_xe': CiscoIosSSH, 'cisco_asa': CiscoAsaSSH, 'cisco_nxos': CiscoNxosSSH,
                'hp_comware': HPComwareSSH}

platforms = list(CLASS_MAPPER.keys())
platforms.sort()
platforms_str = u"\n".join(platforms)


def connect(*args, **kwargs):
    """Factory function selects the proper class and creates object based on device_type."""
    if kwargs['device_type'] not in platforms:
        raise ValueError('Unsupported device_type: '
                         'currently supported platforms are: {0}'.format(platforms_str))
    connection_class = CLASS_MAPPER[kwargs['device_type']]
    return connection_class(*args, **kwargs)
