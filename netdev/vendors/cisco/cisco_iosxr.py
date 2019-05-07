from netdev.exceptions import CommitError
from netdev.logger import logger
from netdev.vendors.ios_like import IOSLikeDevice


class CiscoIOSXR(IOSLikeDevice):
    """Class for working with Cisco IOS XR"""

    _commit_command = 'commit'
    """Command for committing changes"""

    _commit_comment_command = 'commit comment {}'
    """Command for committing changes with comment"""

    _abort_command = "abort"
    """Command for aborting all changes and exit to privilege mode"""

    _show_config_failed = "show configuration failed"
    """Command for showing the reason of failed commit"""

    _show_commit_changes = "show configuration commit changes"
    """Command for showing the other commit which have occurred during our session"""

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

        if config_commands is None:
            return ''

        # Send config commands
        output = await self.config_mode()
        output += await super(IOSLikeDevice, self).send_config_set(config_commands=config_commands)
        if with_commit:
            commit = type(self)._commit_command
            if commit_comment:
                commit = type(self)._commit_comment_command.format(commit_comment)

            self._stdin.write(self._normalize_cmd(commit))
            output += await self._read_until_prompt_or_pattern(r"Do you wish to proceed with this commit anyway\?")
            if 'Failed to commit' in output:
                show_config_failed = type(self)._show_config_failed
                reason = await self.send_command(self._normalize_cmd(show_config_failed))
                raise CommitError(self._host, reason)
            if 'One or more commits have occurred' in output:
                show_commit_changes = type(self)._show_commit_changes
                self._stdin.write(self._normalize_cmd("no"))
                reason = await self.send_command(self._normalize_cmd(show_commit_changes))
                raise CommitError(self._host, reason)

        if exit_config_mode:
            output += await self.exit_config_mode()

        output = self._normalize_linefeeds(output)
        logger.debug("Host {}: Config commands output: {}".format(self._host, repr(output)))
        return output

    async def exit_config_mode(self):
        """Exit from configuration mode"""
        logger.info('Host {}: Exiting from configuration mode'.format(self._host))
        output = ''
        exit_config = type(self)._config_exit
        if await self.check_config_mode():
            self._stdin.write(self._normalize_cmd(exit_config))
            output = await self._read_until_prompt_or_pattern(r"Uncommitted changes found")
            if "Uncommitted changes found" in output:
                self._stdin.write(self._normalize_cmd("no"))
                output += await self._read_until_prompt()
            if await self.check_config_mode():
                raise ValueError("Failed to exit from configuration mode")
        return output

    async def _cleanup(self):
        """ Any needed cleanup before closing connection """
        abort = type(self)._abort_command
        abort = self._normalize_cmd(abort)
        self._stdin.write(abort)
        logger.info("Host {}: Cleanup session".format(self._host))
