"""
Cisco Terminal-Modes Module
"""

from netdev.logger import logger
from .base import BaseTerminalMode


class EnableMode(BaseTerminalMode):
    _name = 'enable_mode'

    async def enter(self):
        logger.info("Host {}: Entering to {}".format(self.device.host, self._name))
        if await self.check():
            return ""
        output = await self.device.send_command(self._enter_command, pattern="Password")
        if "Password" in output:
            await self.device.send_command(self.device._secret)
        if not await self.check():
            raise ValueError("Failed to enter to %s" % self._name)
        self.device.current_terminal = self
        return output


class ConfigMode(BaseTerminalMode):
    _name = 'config_mode'
    pass


class IOSxrConfigMode(ConfigMode):
    async def exit(self):
        """Exit from configuration mode"""
        logger.info("Host {}: Exiting from configuration mode".format(self.device.host))

        if not await self.check():
            return ""
        output = await self.device.send_command(self._exit_command,
                                                pattern=r"Uncommitted changes found")
        if "Uncommitted changes found" in output:
            output += await self.device.send_command("no")

        if await self.check(force=True):
            raise ValueError("Failed to exit from configuration mode")
        self.device.current_terminal = self._parent
        return output
