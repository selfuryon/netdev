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
   - device_type: fujitsu_switch
     host: 3.3.3.3
     password: ****
     username: ****
   - device_type: hp_comware
     host: 4.4.4.4
     password: ****
     username: ****
   - device_type: hp_comware_limited
     host: 5.5.5.5
     password: ****
     username: ****
     cmdline_password: '512900'
   - device_type: arista_eos
     host: 6.6.6.6
     password: ****
     username: ****
   - device_type: juniper_junos
     host: 7.7.7.7
     password: ****
     username: ****

ASA example
-----------
.. literalinclude:: ../examples/cisco_asa.py

NX-OS example
-------------
.. literalinclude:: ../examples/cisco_nxos.py

IOS example
-----------
.. literalinclude:: ../examples/cisco_ios.py

IOS XR example
--------------
.. literalinclude:: ../examples/cisco_iosxr.py

Fujitsu example
---------------
.. literalinclude:: ../examples/fujitsu_switch.py

Comware example
---------------
.. literalinclude:: ../examples/hp_comware.py

Comware Limited example
-----------------------
.. literalinclude:: ../examples/hp_comware_limited.py

Mikrotik RouterOS example
-------------------------
.. literalinclude:: ../examples/mikrotik_routeros.py

Arista EOS example
------------------
.. literalinclude:: ../examples/arista_eos.py

Aruba AOS 6.X example
---------------------
.. literalinclude:: ../examples/aruba_aos_6.py

Juniper JunOS example
---------------------
.. literalinclude:: ../examples/juniper_junos.py

Terminal example
----------------
.. literalinclude:: ../examples/terminal.py