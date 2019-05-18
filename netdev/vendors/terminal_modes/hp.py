"""
Hp Terminal Modes
"""
from netdev.logger import logger
from .base import BaseTerminalMode


class SystemView(BaseTerminalMode):
    """ System View Terminal mode """
    _name = 'system_view'
    pass


class CmdLineMode:
    """ CmdLine Terminal Mode """
    _name = 'cmdline'

    def __init__(self,
                 enter_command,
                 check_error_string,
                 password,
                 device):
        self._enter_command = enter_command
        self._check_error_string = check_error_string
        self._password = password
        self.device = device

    def __call__(self, *args, **kwargs):
        return self.enter()

    async def enter(self):
        """Entering to cmdline-mode"""
        logger.info("Host {}: Entering to cmdline mode".format(self.device.host))

        output = await self.device.send_command(self._enter_command, pattern="\[Y\/N\]")
        output += await self.device.send_command("Y", pattern="password\:")
        output += await self.device.send_command(self._password)

        logger.debug(
            "Host {}: cmdline mode output: {}".format(self.device.host, repr(output))
        )
        logger.info("Host {}: Checking cmdline mode".format(self.device.host))
        if self._check_error_string in output:
            raise ValueError("Failed to enter to cmdline mode")
        self.device.current_terminal = self

        return output
