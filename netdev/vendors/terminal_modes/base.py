"""
Terminal Modes Classes, which handle entering and exist to
different terminal modes
"""
from netdev.logger import logger


class BaseTerminalMode:
    """ Base Terminal Mode """
    _name = ''

    def __init__(self,
                 enter_command,
                 exit_command,
                 check_string,
                 device,
                 parent=None):
        """

        :param enter_command: Command to enter to the terminal mode (ex: conf t)
        :param exit_command: Command to exist the terminal mode (ex: end)
        :param check_string: string to check if the device in this terminal mode
        :param device: Device Object
        :param parent: parent Terminal, for example the enable mode is parent of config mode
        :type BaseTerminalMode
        """
        self._enter_command = enter_command
        self._exit_command = exit_command
        self._check_string = check_string
        self.device = device
        self._parent = parent

    def __eq__(self, other):
        """ Compare different terminal objects """
        return isinstance(self, other) and self.name == other.name

    async def __call__(self):
        """ callable terminal to enter """
        return await self.enter()

    async def check(self, force=False):
        """Check if are in configuration mode. Return boolean"""
        logger.info("Host {}: Checking {}".format(self.device.host, self._name))
        if self.device.current_terminal is not None and not force:
            if self.device.current_terminal._name == self._name:
                return True
        output = await self.device.send_new_line()
        return self._check_string in output

    async def enter(self):
        """ enter terminal mode """
        logger.info("Host {}: Entering to {}".format(self.device.host, self._name))
        if await self.check():
            return ""
        output = await self.device.send_command(self._enter_command, pattern="Password")
        if not await self.check():
            raise ValueError("Failed to enter to %s" % self._name)
        self.device.current_terminal = self
        return output

    async def exit(self):
        """ exit terminal mode """
        logger.info("Host {}: Exiting from {}".format(self.device.host, self._name))
        if not await self.check():
            return ""
        if self.device.current_terminal._name != self._name:
            return ""

        output = await self.device.send_command(self._exit_command)
        if await self.check(force=True):
            raise ValueError("Failed to Exit from %s" % self._name)
        self.device.current_terminal = self._parent
        return output

    async def send_command(self,
                           command_string,
                           pattern="",
                           re_flags=0,
                           strip_command=True,
                           strip_prompt=True,
                           ):
        """ API to send commands on this terminal """
        await self.enter()

        output = await self.device.send_command(
            command_string,
            pattern,
            re_flags,
            strip_command,
            strip_prompt,
        )
        return output
