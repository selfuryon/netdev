"""
Cisco Terminal-Modes Module
"""

from .base import BaseTerminalMode


class EnableMode(BaseTerminalMode):
    """ Cisco Like Enable Mode Class """
    name = 'enable_mode'

    async def enter(self):
        """ Enter Enable Mode """
        self._logger.info("Host {}: Entering to {}".format(self.device.host, self.name))
        if await self.check():
            return ""
        output = await self.device.send_command(self._enter_command, pattern="Password")
        if "Password" in output:
            await self.device.send_command(self.device.secret)
        if not await self.check():
            raise ValueError("Failed to enter to {}".format(self.name))
        self.device.current_terminal = self
        return output


class ConfigMode(BaseTerminalMode):
    """ Cisco Like Config Mode """
    name = 'config_mode'
    pass


class IOSxrConfigMode(ConfigMode):
    """ Cisco IOSxr Config Mode """

    async def exit(self):
        """Exit from configuration mode"""
        self._logger.info("Host {}: Exiting from configuration mode".format(self.device.host))

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
