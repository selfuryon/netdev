import logging
import re

from netdev.netdev_base import NetDevSSH


class FujitsuSwitchSSH(NetDevSSH):
    async def connect(self):
        """
        Async Connection method

        Usual using 4 functions:
            establish_connection() for connecting to device
            set_base_prompt() for finding and setting device prompt
            enable() for getting privilege exec mode
            disable_paging() for non interact output in commands
        """
        await self._establish_connection()
        await self._set_base_prompt()
        await self._enable()
        await self._disable_paging('no pager')

    @property
    def _priv_prompt_term(self):
        return '#'

    @property
    def _unpriv_prompt_term(self):
        return '>'

    async def _set_base_prompt(self):
        """
        Setting two important vars
            base_prompt - textual prompt in CLI (usually hostname)
            base_pattern - regexp for finding the end of command. IT's platform specific parameter

        For Fujitsu devices base_pattern is "(prompt) (\(.*?\))?[>|#]"
        """
        logging.info("In set_base_prompt")
        prompt = await self._find_prompt()
        # Strip off trailing terminator
        self.base_prompt = prompt[1:-3]
        self._base_pattern = r"\({0}\) (\(.*?\))?[{1}|{2}]".format(re.escape(self.base_prompt),
                                                                   re.escape(self._priv_prompt_term),
                                                                   re.escape(self._unpriv_prompt_term))
        logging.debug("Base Prompt is {0}".format(self.base_prompt))
        logging.debug("Base Pattern is {0}".format(self._base_pattern))
        return self.base_prompt

    async def _config_mode(self, config_command='config', exit_config_mode=True):
        """Enter configuration mode."""
        return await super(FujitsuSwitchSSH, self)._config_mode(config_command=config_command)

    @staticmethod
    def _normalize_linefeeds(a_string):
        """
        Convert '\r\r\n','\r\n', '\n\r' to '\n and remove extra '\n\n' in the text
        """
        newline = re.compile(r'(\r\r\n|\r\n|\n\r)')
        return newline.sub('\n', a_string).replace('\n\n', '\n')
