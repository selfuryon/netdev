import re

from ..cisco_like import CiscoLikeDevice
from ..logger import logger


class FujitsuSwitch(CiscoLikeDevice):
    """Class for working with Fujitsu Blade switch"""
    async def _set_base_prompt(self):
        """
        Setting two important vars
            base_prompt - textual prompt in CLI (usually hostname)
            base_pattern - regexp for finding the end of command. IT's platform specific parameter

        For Fujitsu devices base_pattern is "(prompt) (\(.*?\))?[>|#]"
        """
        logger.info("Host {}: Setting base prompt".format(self._host))
        prompt = await self._find_prompt()
        # Strip off trailing terminator
        self._base_prompt = prompt[1:-3]
        delimeter1 = self._get_default_command('delimeter1')
        delimeter2 = self._get_default_command('delimeter2')
        pattern = self._get_default_command('pattern')
        self._base_pattern = pattern.format(re.escape(self._base_prompt[:12]), re.escape(delimeter1),
                                            re.escape(delimeter2))
        logger.debug("Host {}: Base Prompt: {}".format(self._host, self._base_prompt))
        logger.debug("Host {}: Base Pattern: {}".format(self._host, self._base_pattern))
        return self._base_prompt

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
            'delimeter1': '>',
            'delimeter2': '#',
            'pattern': r"\({}.*?\) (\(.*?\))?[{}|{}]",
            'disable_paging': 'no pager',
            'priv_enter': 'enable',
            'priv_exit': 'disable',
            'config_enter': 'conf',
            'config_exit': 'end',
            'config_check': ')#',
        }
        # @formatter:on
        return command_mapper[command]
