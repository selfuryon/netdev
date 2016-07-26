.. module:: netdev

.. _API:

API Documentation
*****************

Overview
========

Netdev is an asynchronous library for working with network devices. For each vendor you should use separate class for
working. For this purpose are used Factory method :func:`connect`. In params for this method you should specify
device_type for correct working.
Sample of working is:

.. code-block:: python

   async def working_with_netdev():
      dev = netdev.connect(host='host', username='username', password='password', device_type='device_type')
      await dev.connect() # Connecting and preparing session for working
      output = await dev.send_command('command') # working with command in privilege/user mode
      print(output)
      output = await dev.send_config_set(['first_command','second_command'] #working with commands in config mode
      print(output)
      await dev.disconnect() #disconnecting from device

   loop = asyncio.get_event_loop()
   loop.run_until_complete(working_with_netdev())

Public API
.. autofunction:: connect

Classes
=======

.. autoclass:: netdev.netdev_base.NetDev
   :members:
   :special-members: __init__


