"""Subclass specific to Cisco ASA."""

import logging
import re

from netdev.netdev_base import NetDev


class CiscoAsa(NetDev):
    """Subclass specific to Cisco ASA."""

    def __init__(self, host=u'', username=u'', password=u'', secret=u'', port=22, device_type=u'', known_hosts=None,
                 local_addr=None, client_keys=None, passphrase=None):
        super().__init__(host=host, username=username, password=password, secret=secret, port=port,
                         device_type=device_type, known_hosts=known_hosts, local_addr=local_addr,
                         client_keys=client_keys, passphrase=passphrase)
        self.current_context = 'system'
        self.mode_multiple = False

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
        await self._check_context()

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
        logging.info("In set_base_prompt")
        prompt = await self._find_prompt()
        context = 'system'
        # Cut off prompt from "prompt/context"
        if '/' in prompt:
            prompt, context = prompt[:-1].split('/')
        else:
            prompt = prompt[:-1]
        self.base_prompt = prompt
        self.current_context = context
        priv_prompt = self._get_default_command('priv_prompt')
        unpriv_prompt = self._get_default_command('unpriv_prompt')
        self._base_pattern = r"{}(\/\w+)?(\(.*?\))?[{}|{}]".format(re.escape(self.base_prompt), re.escape(priv_prompt),
                                                                   re.escape(unpriv_prompt))
        logging.debug("Base Prompt is {0}".format(self.base_prompt))
        logging.debug("Base Pattern is {0}".format(self._base_pattern))
        logging.debug("Current Context is {0}".format(self.current_context))
        return self.base_prompt

    async def _check_context(self):
        """
        Check mode multiple. If mode is multiple we adding info about contexts
        """
        logging.info("In check_context")
        out = await self.send_command('show mode')
        if 'multiple' in out:
            self.mode_multiple = True

        logging.debug("context mode is {}".format(self.mode_multiple))

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
