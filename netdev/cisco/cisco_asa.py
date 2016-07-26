"""Subclass specific to Cisco ASA."""

import re

from netdev.logger import logger
from netdev.netdev_base import NetDev


class CiscoAsa(NetDev):
    """Subclass specific to Cisco ASA."""

    def __init__(self, host=u'', username=u'', password=u'', secret=u'', port=22, device_type=u'', known_hosts=None,
                 local_addr=None, client_keys=None, passphrase=None):
        super().__init__(host=host, username=username, password=password, secret=secret, port=port,
                         device_type=device_type, known_hosts=known_hosts, local_addr=local_addr,
                         client_keys=client_keys, passphrase=passphrase)
        self._current_context = 'system'
        self._multiple_mode = False

    @property
    def current_context(self):
        """ Returning current context for ASA"""
        return self._current_context

    @property
    def multiple_mode(self):
        """ Returning Bool True if ASA in multiple mode"""
        return self._multiple_mode

    async def connect(self):
        """
        Async Connection method

        Usual using 4 functions:
            establish_connection() for connecting to device
            set_base_prompt() for finding and setting device prompt
            enable() for getting privilege exec mode
            disable_paging() for non interact output in commands
        """
        logger.info("Connecting to device")
        await self._establish_connection()
        await self._set_base_prompt()
        await self._enable()
        await self._disable_paging()
        await self._check_multiple_mode()
        logger.info("Connected to device")

    async def send_command(self, command_string, strip_prompt=True, strip_command=True):
        """
        If the ASA is in multi-context mode, then the base_prompt needs to be
        updated after each context change.
        """
        output = await super(CiscoAsa, self).send_command(command_string=command_string, strip_prompt=strip_prompt,
                                                          strip_command=strip_command)
        if "changet" in command_string:
            await self._set_base_prompt()
        return output

    async def _set_base_prompt(self):
        """
        Setting three important vars for ASA
            base_prompt - textual prompt in CLI (usually hostname)
            base_pattern - regexp for finding the end of command. IT's platform specific parameter
            context - current context for ASA. If ASA in single mode, context = system

        For ASA devices base_pattern is "prompt(\/\w+)?(\(.*?\))?[#|>]
        """
        logger.info("Setting base prompt")
        prompt = await self._find_prompt()
        context = 'system'
        # Cut off prompt from "prompt/context"
        if '/' in prompt:
            prompt, context = prompt[:-1].split('/')
        else:
            prompt = prompt[:-1]
        self._base_prompt = prompt
        self._current_context = context
        priv_prompt = self._get_default_command('priv_prompt')
        unpriv_prompt = self._get_default_command('unpriv_prompt')
        self._base_pattern = r"{}.*(\/\w+)?(\(.*?\))?[{}|{}]".format(re.escape(self._base_prompt[:12]),
                                                                     re.escape(priv_prompt), re.escape(unpriv_prompt))
        logger.debug("Base Prompt: {}".format(self._base_prompt))
        logger.debug("Base Pattern: {}".format(self._base_pattern))
        logger.debug("Current Context: {}".format(self._current_context))
        return self._base_prompt

    async def _check_multiple_mode(self):
        """
        Check mode multiple. If mode is multiple we adding info about contexts
        """
        logger.info("Checking multiple mode")
        out = await self.send_command('show mode')
        if 'multiple' in out:
            self._multiple_mode = True

        logger.debug("Multiple mode: {}".format(self._multiple_mode))

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
            'disable_paging': 'terminal pager 0',
            'priv_enter': 'enable',
            'priv_exit': 'enable',
            'config_enter': 'conf t',
            'config_exit': 'end',
            'check_config_mode': ')#'
        }
        # @formatter:on
        return command_mapper[command]
