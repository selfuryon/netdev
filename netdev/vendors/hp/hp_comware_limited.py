from netdev.logger import logger
from netdev.vendors.comware_like import ComwareLikeDevice


class HPComwareLimited(ComwareLikeDevice):
    """Class for working with HP Comware Limited like 1910 and 1920 models"""

    def __init__(self, cmdline_password=u'', *args, **kwargs):
        """
        Initialize  class for asynchronous working with network devices

        :param str host: device hostname or ip address for connection
        :param str username: username for logging to device
        :param str password: user password for logging to device
        :param str cmdline_password: password for entering to _cmd_line
        :param int port: ssh port for connection. Default is 22
        :param str device_type: network device type
        :param known_hosts: file with known hosts. Default is None (no policy). With () it will use default file
        :param str local_addr: local address for binding source of tcp connection
        :param client_keys: path for client keys. Default in None. With () it will use default file in OS
        :param str passphrase: password for encrypted client keys
        :param float timeout: timeout in second for getting information from channel
        :param loop: asyncio loop object
        """
        super().__init__(*args, **kwargs)
        self._cmdline_password = cmdline_password

    _cmdline_mode_enter_command = '_cmdline-mode on'
    """Command for entering to cmdline model"""

    _cmdline_mode_check = 'Invalid password'
    """Checking string for wrong password in trying of entering to cmdline mode"""

    async def connect(self):
        """
        Basic asynchronous connection method

        It connects to device and makes some preparation steps for working.
        Usual using 4 functions:

        * _establish_connection() for connecting to device
        * _set_base_prompt() for finding and setting device prompt
        * _cmdline_mode_enter() for entering hidden full functional mode
        * _disable_paging() for non interact output in commands
        """
        logger.info("Host {}: Trying to connect to the device".format(self._host))
        await self._establish_connection()
        await self._set_base_prompt()
        await self._cmdline_mode_enter()
        await self._disable_paging()
        logger.info("Host {}: Has connected to the device".format(self._host))

    async def _cmdline_mode_enter(self):
        """Entering to cmdline-mode"""
        logger.info('Host {}: Entering to cmdline mode'.format(self._host))
        output = ''
        cmdline_mode_enter = type(self)._cmdline_mode_enter_command
        check_error_string = type(self)._cmdline_mode_check

        output = await self.send_command(cmdline_mode_enter, pattern='\[Y\/N\]')
        output += await self.send_command('Y', pattern='password\:')
        output += await self.send_command(self._cmdline_password)

        logger.debug("Host {}: cmdline mode output: {}".format(self._host, repr(output)))
        logger.info('Host {}: Checking cmdline mode'.format(self._host))
        if check_error_string in output:
            raise ValueError('Failed to enter to cmdline mode')

        return output
