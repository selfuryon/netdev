"""
Factory function for creating netdev classes
"""
from netdev.vendors.cisco.general import initialize_cisco

# @formatter:off
# The keys of this dictionary are the supported device_types
CLASS_MAPPER = {
    "cisco_ios": CiscoIOS,
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
