"""
Copyright (c) 2019 Sergey Yakovlev <selfuryon@gmail.com>.

Vendors unit module
"""
from netdev.vendors.cisco_like import (CiscoCLIModes, cisco_device_manager,
                                       ciscoxr_device_manager)

__all__ = ("cisco_device_manager", "ciscoxr_device_manager", "CiscoCLIModes")
