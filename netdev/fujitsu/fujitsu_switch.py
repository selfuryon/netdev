import logging
import re

from netdev.netdev_base import NetDev


class FujitsuSwitch(NetDev):
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
        await self._disable_paging()

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
        priv_prompt = self._get_default_command('priv_prompt')
        unpriv_prompt = self._get_default_command('unpriv_prompt')
        self._base_pattern = r"\({}.*?\) (\(.*?\))?[{}|{}]".format(re.escape(self.base_prompt[:12]),
                                                                   re.escape(priv_prompt), re.escape(unpriv_prompt))
        logging.debug("Base Prompt is {0}".format(self.base_prompt))
        logging.debug("Base Pattern is {0}".format(self._base_pattern))
        return self.base_prompt

    @staticmethod
    def _normalize_linefeeds(a_string):
        """
        Convert '\r\r\n','\r\n', '\n\r' to '\n and remove extra '\n\n' in the text
        """
        newline = re.compile(r'(\r\r\n|\r\n|\n\r)')
        return newline.sub('\n', a_string).replace('\n\n', '\n')

    def _get_default_command(self, command):
        """
        Returning default commands for device

        :param command: command for returning
        :return: real command for this network device
        """
        # @formatter:off
        command_mapper = {
            'priv_prompt': '#',
            'unpriv_prompt': '>',
            'disable_paging': 'no pager',
            'priv_enter': 'enable',
            'priv_exit': 'disable',
            'config_enter': 'conf',
            'config_exit': 'end',
            'check_config_mode': ')#'
        }
        # @formatter:on
        return command_mapper[command]
