.. module:: netdev

.. _overview:

Library information
*******************

Overview
========
Netdev is asynchronous multi-vendor library for interacting with network devices. So you can create many
simultaneous connection to network devices for parallel executing commands.

For creating connection to network device you should use function :func:`create` like this:

.. code-block:: python

   async def working_with_netdev():
      dev = netdev.create(host='host', username='username', password='password', device_type='device_type')
      await dev.connect() # Connecting and preparing session for working
      output = await dev.send_command('command') # working with command in privilege/user mode
      print(output)
      output = await dev.send_config_set(['first_command','second_command'] #working with commands in config mode
      print(output)
      await dev.disconnect() #disconnecting from device

   loop = asyncio.get_event_loop()
   loop.run_until_complete(working_with_netdev())

or the same with using async context manager:

.. code-block:: python

   async def working_with_netdev():
      async with netdev.create(host='host', username='username', password='password', device_type='device_type') as dev:
          output = await dev.send_command('command') # working with command in privilege/user mode
          print(output)
          output = await dev.send_config_set(['first_command','second_command'] #working with commands in config mode
          print(output)

   loop = asyncio.get_event_loop()
   loop.run_until_complete(working_with_netdev())


Library structure
=================

Library consist from several base classes and end classes which using for communication.
The main class is :class:`BaseDevice`. It provides some basic functionality regardless of device type.
Library also have three common child classes: :class:`IOSLikeDevice`, :class:`ComwareLikeDevice`
and :class:`JunOSLikeDevice`.

:class:`IOSLikeDevice` class provides basic methods for Cisco IOS like devices: devices which have user exec,
privilege exec and conf mode concepts.

:class:`ComwareLikeDevice` class provides basic methods for HP Comware like devices: these devices have only
exec view and system view concepts.

:class:`JunOSLikeDevice` class provides basic methods for Juniper JunOS like devices: they have operation mode and
configuration mode concepts with committing changes.

All other classes are the end classes which you can use for working with particular device:

* :class:`MikrotikRouterOS`
* :class:`CiscoIOS`
* :class:`CiscoIOSXR`
* :class:`CiscoASA`
* :class:`CiscoNXOS`
* :class:`FujitsuSwitch`
* :class:`HPComware`
* :class:`HPComwareLimited`
* :class:`AristaEOS`
* :class:`JuniperJunOS`

The particular class selected by parameter *device_type* in :func:`create`

Logging
=======

For debugging purpose library has :data:`logger` object. You can use it like this:

.. code-block:: python

    import netdev

    netdev_logger = netdev.logger
    netdev_logger.setLevel(logging.INFO)
    netdev_logger.addHandler(logging.StreamHandler())

    #Your own code

Common public methods and properties
====================================

Base classes have several common public methods.

Managing flow
-------------
For working with network device firstly you need to connect to device and after working you need
to disconnect from device. For this purpose are used these methods:

- :func:`BaseDevice.connect`
- :func:`BaseDevice.disconnect`

Sending commands
----------------
Some devices using mode principle: exists exec mode and configuration mode. Exec mode are used for getting some
information from device, configuration mode are used for configuration device. For this purpose netdev
have 2 basic methods:

- :func:`BaseDevice.send_command`

This method is used for sending specific command to device in exec mode. Basically for getting some information
from device

- :func:`BaseDevice.send_config_set`

This method are used for sending command list to device in configuration mode. Command list is the list of all commands
which configure device.


Some others
-----------

- :attr:`BaseDevice.base_prompt`
- :attr:`CiscoASA.current_context`
- :attr:`CiscoASA.multiple_mode`
