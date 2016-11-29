from ..hp_like import HPLikeDevice
from ..logger import logger


class HPComwareLimited(HPLikeDevice):
    """Class for working with HP Comware Limited like 1910 and 1920 models"""

    def __init__(self, host=u'', username=u'', password=u'', secret=u'', cmdline_password='', port=22, device_type=u'',
                 known_hosts=None, local_addr=None, client_keys=None, passphrase=None, loop=None):
        """
        Initialize  class for asynchronous working with network devices

        :param str host: hostname or ip address for connection
        :param str username: username for logger to device
        :param str password: password for user for logger to device
        :param str secret: secret password for privilege mode
        :param int port: ssh port for connection. Default is 22
        :param str device_type: network device type. This is subclasses of this class
        :param known_hosts: file with known hosts. Default is None (no policy). with () it will use default file
        :param str local_addr: local address for binding source of tcp connection
        :param client_keys: path for client keys. With () it will use default file in OS.
        :param str passphrase: password for encrypted client keys
        :param loop: asyncio loop object
        :returns: :class:`HPLikeDevice` Base class for working with hp comware like devices
        """
        super().__init__(host=host, username=username, password=password, secret=secret, port=port,
                         device_type=device_type, known_hosts=known_hosts, local_addr=local_addr,
                         client_keys=client_keys, passphrase=passphrase, loop=loop)

        self._cmdline_password = cmdline_password

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
        logger.info("Host {}: Connecting to device".format(self._host))
        await self._establish_connection()
        await self._set_base_prompt()
        await self._cmdline_mode_enter()
        await self._disable_paging()
        logger.info("Host {}: Connected to device".format(self._host))

    def _get_default_command(self, command):
        """
        Returning default commands for device

        :param str command: command for returning
        :return: real command for this network device
        """
        # @formatter:off
        command_mapper = {
            'delimeter1': '>',
            'delimeter2': ']',
            'delimeter_left1': '<',
            'delimeter_left2': '[',
            'pattern': r"[{}|{}]{}[\-\w]*[{}|{}]",
            'disable_paging': 'screen-length disable',
            'sview_enter': 'system-view',
            'sview_exit': 'return',
            'sview_check': ']',
            'cmdline_mode_enter': '_cmdline-mode on',
            'cmdline_mode_check': 'Invalid password',
        }
        # @formatter:on
        return command_mapper[command]

    async def _cmdline_mode_enter(self):
        """Entering to cmdline-mode"""
        logger.info('Host {}: Entering to cmdline mode'.format(self._host))
        output = ''
        cmdline_mode_enter = self._get_default_command('cmdline_mode_enter')
        check_error_string = self._get_default_command('cmdline_mode_check')

        output = await self.send_command(cmdline_mode_enter, pattern='\[Y\/N\]')
        output += await self.send_command('Y', pattern='password\:')
        output += await self.send_command(self._cmdline_password)

        logger.debug("Host {}: cmdline mode output: {}".format(self._host, output))
        logger.info('Host {}: Checking cmdline mode'.format(self._host))
        if check_error_string in output:
            raise ValueError('Failed to enter to cmdline mode')

        return output
