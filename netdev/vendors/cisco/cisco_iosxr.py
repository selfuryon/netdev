from ..ios_like import IOSLikeDevice
from ..logger import logger


class CiscoIOSXR(IOSLikeDevice):
    """Class for working with Cisco IOS XR"""

    _commit_command = 'commit'
    """Command for committing changes"""

    _commit_comment_command = 'commit comment {}'
    """Command for committing changes with comment"""

    async def send_config_set(self, config_commands=None, with_commit=True, commit_comment='', exit_config_mode=True):
        """
        Sending configuration commands to device
        By default automatically exits/enters configuration mode.

        :param list config_commands: iterable string list with commands for applying to network devices in system view
        :param bool with_commit: if true it commit all changes after applying all config_commands
        :param string commit_comment: message for configuration commit
        :param bool exit_config_mode: If true it will quit from configuration mode automatically
        :return: The output of these commands
        """

        # Send config commands by IOS Like Device
        output = await super().send_config_set(config_commands=config_commands, exit_config_mode=False)
        if with_commit:
            commit = type(self)._commit_command
            if commit_comment:
                commit = type(self)._commit_comment_command.format(commit_comment)

            self._stdin.write(self._normalize_cmd(commit))
            output += await self._read_until_prompt()

        if "Please issue 'show configuration failed" in output:
            reason = await self.send_command('show configuration failed')
            logger.error('Errors applying config: %s', reason)
            output += reason
            if exit_config_mode:
                logger.debug('Aborting uncommitted changes.')
                output += await self.send_command('abort')

        if exit_config_mode:
            output += await self.exit_config_mode()

        output = self._normalize_linefeeds(output)
        logger.debug("Host {}: Config commands output: {}".format(self._host, repr(output)))
        return output
