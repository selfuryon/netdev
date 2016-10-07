.. module:: netdev

.. _Examples:

Examples
********

In examples are used configuration files.
config.yaml:

.. code-block:: text

   device_list: credentials.yaml

credentials.yaml

.. code-block:: text

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

NX-OS example
-------------
.. literalinclude:: ../examples/cisco_nxos_example.py

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
