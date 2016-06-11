import logging
import re

from netdev.netdev_base import NetDevSSH


class HPComwareSSH(NetDevSSH):
    async def connect(self):
        """Prepare the session after the connection has been established."""
        await self.establish_connection()
        await self.set_base_prompt()
        await self.disable_paging()

    @property
    def disable_paging_command(self):
        return "screen-length disable"

    @property
    def priv_prompt_term(self):
        return ']'

    @property
    def unpriv_prompt_term(self):
        return '>'

    @property
    def prompt_pattern(self):
        return r"[\[|<]{0}([\-\w]+)?[{1}|{2}]"

    async def set_base_prompt(self):
        """
        Setting two important vars
            base_prompt - textual prompt in CLI (usually hostname)
            base_pattern - regexp for finding the end of command. IT's platform specific parameter

        For Comware devices base_pattern is "[\]|>]prompt(\-\w+)?[\]|>]
        """
        logging.info("In set_base_prompt")
        prompt = await self.find_prompt()
        # Strip off trailing terminator
        self._base_prompt = prompt[1:-1]
        self._base_pattern = self.prompt_pattern.format(re.escape(self._base_prompt), re.escape(self.priv_prompt_term),
                                                        re.escape(self.unpriv_prompt_term))
        logging.debug("Base Prompt is {0}".format(self._base_prompt))
        logging.debug("Base Pattern is {0}".format(self._base_pattern))
        return self._base_prompt

    async def config_mode(self, config_command='system-view', exit_config_mode=True):
        """Enter configuration mode."""
        return await super(HPComwareSSH, self).config_mode(config_command=config_command)

    async def exit_config_mode(self, exit_config='return', pattern=''):
        """Exit config mode."""
        return await super(HPComwareSSH, self).exit_config_mode(exit_config=exit_config)

    async def check_config_mode(self, check_string=']', pattern=''):
        """Check whether device is in configuration mode. Return a boolean."""
        return await super(HPComwareSSH, self).check_config_mode(check_string=check_string)
