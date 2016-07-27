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

Examples
========
In examples are used configuration files.
config.yaml:

.. code-block:: yaml

   device_list: credentials.yaml

credentials.yaml

.. code-block:: yaml

   - device_type: cisco_asa
     host: 1.1.1.1
     password: ****
     username: ****
   - device_type: cisco_ios
     host: 2.2.2.2
     password: ****
     username: ****
   - device_type: cisco_ios
     host: 3.3.3.3
     password: ****
     username: ****
   - device_type: hp_comware
     host: 4.4.4.4
     password: ****
     username: ****

ASA example
-----------
.. literalinclude:: ../examples/cisco_asa_example.py

IOS example
-----------
.. literalinclude:: ../examples/cisco_ios_example.py

Fujitsu example
---------------
.. literalinclude:: ../examples/fujitsu_switch_example.py

Comware example
---------------
.. literalinclude:: ../examples/hp_comware_example.py

Mikrotik example
----------------
.. literalinclude:: ../examples/mikrotik_routeros_example.py