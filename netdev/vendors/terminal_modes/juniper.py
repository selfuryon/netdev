"""
Juniper Terminal Modes
"""
from .base import BaseTerminalMode
from .cisco import ConfigMode as CiscoConfigMode


class ConfigMode(CiscoConfigMode):
    pass


class CliMode(BaseTerminalMode):
    name = 'cli_mode'

    def exit(self):
        pass
