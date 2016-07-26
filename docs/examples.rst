Examples
********

Sample for work with network device:

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

Some examples
=============
ASA
---
.. literalinclude:: ../examples/cisco_asa_example.py

IOS
---
.. literalinclude:: ../examples/cisco_ios_example.py

Fujitsu
-------
.. literalinclude:: ../examples/fujitsu_switch_example.py

Comware
-------
.. literalinclude:: ../examples/hp_comware_example.py

Mikrotik
--------
.. literalinclude:: ../examples/mikrotik_routeros_example.py