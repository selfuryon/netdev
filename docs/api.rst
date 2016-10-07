.. module:: netdev

.. _API:

API Documentation
*****************

Overview
========

For each vendor you should use separate class for working.
For this purpose are used Factory method :func:`create`. In params for this method you should specify device_type
for taking right class


Factory method
==============

.. autofunction:: create

Classes
=======

Base classes:
-------------
These classes are abstract and used as parent by other classes:

.. autoclass:: BaseDevice
   :members:
   :special-members: __init__

.. autoclass:: CiscoLikeDevice
   :members:

.. autoclass:: HPLikeDevice
   :members:

End classes
-----------

.. autoclass:: CiscoAsa
   :members:

.. autoclass:: CiscoIos
   :members:

.. autoclass:: CiscoNxos
   :members:

.. autoclass:: FujitsuSwitch
   :members:

.. autoclass:: HPComware
   :members:

.. autoclass:: MikrotikRouterOS
   :members:



