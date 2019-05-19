from netdev.vendors.terminal_modes.juniper import CliMode
from netdev.vendors.devices.junos_like import JunOSLikeDevice


class JuniperJunOS(JunOSLikeDevice):
    """Class for working with Juniper JunOS"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cli_mode = CliMode(
            enter_command=type(self)._cli_command,
            check_string=type(self)._cli_check,
            exit_command='',
            device=self
        )

    _cli_check = ">"
    """Checking string for shell mode"""

    _cli_command = "cli"
    """Command for entering to cli mode"""

    async def _session_preparation(self):
        await self.cli_mode()
        await super()._session_preparation()
