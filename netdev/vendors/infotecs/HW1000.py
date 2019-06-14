"""
HW1000 is a class for working with Vipnet HW1000 crypto gateways
"""
import re
from netdev.logger import logger
from netdev.vendors.base import BaseDevice

class HW1000(BaseDevice):
    """
    Class for working with Vipnet HW1000
    
    HW1000 devices have three administration modes:
    *user exec or unprivileged exec. This mode allows you perform basic tests and get system information.
    *privilege exec. This mode allows all EXEC mode commands available on the system. HW100 supports
        only one active privilege session. Use preempt_privilege=True to close current privilege session
    *shell. This mode exits standart device shell and enters Linux shell 
    """
    def __init__(self, secret=u'',preempt_privilege=False, *args, **kwargs):
        """
        Initialize class for asynchronous working with network devices
        :param str host: device hostname or ip address for connection
        :param str username: username for logging to device
        :param str password: user password for logging to device
        :param str secret: secret password for privilege mode
        :param bool preempt_privilege: close current privilige session (if exists). Default is False
        :param int port: ssh port for connection. Default is 22
        :param str device_type: network device type
        :param known_hosts: file with known hosts. Default is None (no policy). With () it will use default file
        :param str local_addr: local address for binding source of tcp connection
        :param client_keys: path for client keys. Default in None. With () it will use default file in OS
        :param str passphrase: password for encrypted client keys
        :param float timeout: timeout in second for getting information from channel
        :param loop: asyncio loop object
        """
        self._secret = secret
        self._preempt_privilege = preempt_privilege

        super().__init__(*args, **kwargs)

    _priv_enter = 'enable'
    """Command for entering to privilege exec"""

    _priv_exit = 'exit'
    """Command for existing from privilege exec to user exec"""

    _priv_check = '#'
    """Checking string in prompt. If it's exist im prompt - we are in privilege exec"""

    _priv_confirm_message = "Are you sure you want to force termination of the specified session"
    """Confirmation message for privilege preemtion""" 

    _shell_enter = "admin esc"
    """Command for entering Linux shell"""
    
    _shell_exit = "exit"
    """Command for exiting Linux shell"""

    _shell_check = "sh"
    """Checking string in prompt. If it's exist im prompt - we are in Linux shell"""

    _shell_enter_message = "Are you sure you want to exit to the Linux system shell?"
    """Confirmation message for entering Linux shell"""

    async def connect(self):
        """
        Basic asynchronous connection method for HW1000 devices

        It connects to device and makes some preparation steps for working.
        Usual using 3 functions:

        * _establish_connection() for connecting to device
        * _set_base_prompt() for finding and setting device prompt
        * _enable() for getting privilege exec mode
        """
        logger.info("Host {}: Trying to connect to the device".format(self._host))
        await self._establish_connection()
        await self._set_base_prompt()
        await self.enable_mode()
        logger.info("Host {}: Has connected to the device".format(self._host))

    async def check_enable_mode(self):
        """Check if we are in privilege exec. Return boolean"""
        logger.info('Host {}: Checking privilege exec'.format(self._host))
        check_string = type(self)._priv_check
        self._stdin.write(self._normalize_cmd('\n'))
        output = await self._read_until_prompt()
        return check_string in output

    async def enable_mode(self, pattern='password', re_flags=re.IGNORECASE):
        """Enter to privilege exec"""
        logger.info('Host {}: Entering to privilege exec'.format(self._host))
        output = ""
        enable_command = type(self)._priv_enter
        if not await self.check_enable_mode():
            self._stdin.write(self._normalize_cmd(enable_command))
            output += await self._read_until_prompt_or_pattern(
                pattern=pattern, re_flags=re_flags)
            if re.search(pattern, output, re_flags):
                self._stdin.write(self._normalize_cmd(self._secret))
                output += await self._read_until_prompt_or_pattern(
                    pattern=type(self)._priv_confirm_message,re_flags=re_flags)
                if re.search(type(self)._priv_confirm_message,output,re_flags):
                    if self._preempt_privilege:
                        self._stdin.write(self._normalize_cmd("Yes"))
                    else:
                        raise ValueError("Failed to enter privilege exec:"
                        "there is already a active administration session."
                        "Use preempt_privilege=True")
            if not await self.check_enable_mode():
                raise ValueError("Failed to enter to privilege exec")
        return output

    async def exit_enable_mode(self):
        """Exit from privilege exec"""
        logger.info('Host {}: Exiting from privilege exec'.format(self._host))
        output = ""
        exit_enable = type(self)._priv_exit
        if await self.check_enable_mode():
            self._stdin.write(self._normalize_cmd(exit_enable))
            output += await self._read_until_prompt()
            if await self.check_enable_mode():
                raise ValueError("Failed to exit from privilege exec")
        return output

    async def check_shell_mode(self):
        """Checks if device in shell mode or not"""
        logger.info('Host {}: Checking shell mode'.format(self._host))
        check_string = type(self)._shell_check
        self._stdin.write(self._normalize_cmd('\n'))
        output = await self._read_until_pattern(r'[\>|\#]')
        logger.info(output)
        return check_string in output
    
    async def enter_shell_mode(self,re_flags=re.IGNORECASE):
        """ Enter into shell mode"""
        logger.info('Host {}: Entering to shell mode'.format(self._host))
        output = ''
        shell_command = type(self)._shell_enter
        if not await self.check_shell_mode():
            self._stdin.write(self._normalize_cmd(shell_command))
            output += await self._read_until_pattern(
                pattern=type(self)._shell_enter_message,re_flags=re_flags)
            self._stdin.write(self._normalize_cmd("Yes"))
            output += await self._read_until_pattern('password:', re_flags=re_flags)
            self._stdin.write(self._normalize_cmd(self._secret))
            output += await self._read_until_pattern(r'[\>|\#]')
            await self._set_base_prompt() # base promt differs in shell mode
            if not await self.check_shell_mode():
                raise ValueError('Failed to enter to shell mode')
        return output
    
    async def exit_shell_mode(self):
        """Exit from shell mode"""
        logger.info('Host {}: Exiting from shell mode'.format(self._host))
        output = ''
        exit_shell = type(self)._shell_exit
        if await self.check_shell_mode():
            self._stdin.write(self._normalize_cmd(exit_shell))
            output = await self._read_until_pattern(r'[\>|\#]')
            if await self.check_shell_mode():
                raise ValueError("Failed to exit from shell mode")
            await self._set_base_prompt() # base promt differs in shell mode
        return output
    
    async def _cleanup(self):
        """ Any needed cleanup before closing connection """
        logger.info("Host {}: Cleanup session".format(self._host))
        await self.exit_shell_mode()
        await self.exit_enable_mode()
        