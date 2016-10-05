.. module:: netdev

.. _overview:

Library information
*******************

Overview
========
Netdev is asynchronous multi-vendor library for interacting with network devices. So you can create many
simultaneous connection to network devices for parallel executing commands.

For creating connection to network device you should use :func:`create` like this:

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

or with using async context manager:

.. code-block:: python

   async def working_with_netdev():
      async with netdev.create(host='host', username='username', password='password', device_type='device_type') as dev:
          output = await dev.send_command('command') # working with command in privilege/user mode
          print(output)
          output = await dev.send_config_set(['first_command','second_command'] #working with commands in config mode
          print(output)

   loop = asyncio.get_event_loop()
   loop.run_until_complete(working_with_netdev())

Public methods and properties
=============================

For interacting with specific device are used specific class: :func:`create` is a factory method for
creating specific class object. Basically it has several methods and properties:


Managing flow
-------------
For working with network device firstly you need to connect to device and after working you need
to disconnect from device. For this purpose are used these methods:

**Method :func:`connect`**
.. autofunction:: base.connect

**Method :func:`disconnect`**
.. autofunction:: base.disconnect


Sending commands
----------------
Some devices using mode principles: exists exec mode and configuration mode. Exec mode are used for getting some
information from device, configuration mode are used for configuration device. For this purpose netdev
have 2 basic methods:

**Method :func:`send_command`**
.. autofunction:: base.send_command

This method is used for sending specific command to device in exec mode. Basically for getting some information
from device

**Method :func:`send_config_set`**
.. autofunction:: base.send_config_set

This method are used for sending command list to device in configuration mode. Command list is the list of all commands
which configure device.