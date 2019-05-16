from netdev.logger import logger


class TerminalMode:
    def __init__(self,
                 enter_command,
                 exit_command,
                 check_string,
                 name,
                 device):
        self._name = name
        self._enter_command = enter_command
        self._exit_command = exit_command
        self._check_string = check_string
        self._name = name
        self._device = device

    def __eq__(self, other):
        return isinstance(self, other) and self.name == other.name

    async def check(self):
        """Check if are in configuration mode. Return boolean"""
        logger.info("Host {}: Checking {}".format(self._device.host, self._name))
        output = await self._device.send_new_line()
        return self._check_string in output

    async def enter(self):
        logger.info("Host {}: Entering to {}".format(self._device.host, self._name))
        if self._device.current_terminal == self:
            return ""

        output = await self._device.send_command_line(self._enter_command)
        if not await self.check():
            raise ValueError("Failed to enter to %s" % self._name)
        self._device.current_terminal = self
        return output

    async def exit(self):
        logger.info("Host {}: Exiting from {}".format(self._device.host, self._name))
        if self._device.current_terminal != self:
            return ""
        output = await self._device.send_command_line(self._exit_command)
        if await self.check():
            raise ValueError("Failed to Exit from %s" % self._name)
        self._device.current_terminal = self
        return output


# class IOSXRConfigMode(TerminalMode):
#
#     async def exit(self):
#         """Exit from configuration mode"""
#         logger.info("Host {}: Exiting from configuration mode".format(self.host))
#         output = ""
#
#         if await self.check():
#             self._stdin.write(self._normalize_cmd())
#             output = await self._device._read_until_prompt_or_pattern(
#                 r"Uncommitted changes found"
#             )
#             if "Uncommitted changes found" in output:
#                 self._stdin.write(self._normalize_cmd("no"))
#                 output += await self._read_until_prompt()
#             if await self.check_config_mode():
#                 raise ValueError("Failed to exit from configuration mode")
#         return output
