"""Subclass specific to Cisco ASA."""

import logging
import re

from netdev.netdev_base import NetDevSSH


class CiscoAsaSSH(NetDevSSH):
    """Subclass specific to Cisco ASA."""

    def __init__(self, ip=u'', host=u'', username=u'', password=u'', secret=u'', port=22, device_type=u'',
                 ssh_strict=False):
        super().__init__(ip, host, username, password, secret, port, device_type, ssh_strict)
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
        await self._disable_paging(command='terminal pager 0')
        await self._check_context()

    async def send_command(self, command_string, strip_prompt=True, strip_command=True):
        """
        If the ASA is in multi-context mode, then the base_prompt needs to be
        updated after each context change.
        """
        output = await super(CiscoAsaSSH, self).send_command(command_string, strip_prompt, strip_command)
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
        self._base_pattern = r"{0}(\/\w+)?(\(.*?\))?[{1}|{2}]".format(re.escape(self.base_prompt),
                                                                      re.escape(self._priv_prompt_term),
                                                                      re.escape(self._unpriv_prompt_term))
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
