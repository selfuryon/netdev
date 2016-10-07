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

Base classes
------------
These classes are abstract and used as parent by other classes:

BaseDevice
~~~~~~~~~~

.. autoclass:: BaseDevice
   :members:
   :special-members: __init__

CiscoLikeDevice
~~~~~~~~~~~~~~~

.. autoclass:: CiscoLikeDevice
   :members:
   :inherited-members:

HPLikeDevice
~~~~~~~~~~~~

.. autoclass:: HPLikeDevice
   :members:
   :inherited-members:

End classes
-----------
These classes are using for particular connection to end devices

CiscoIOS
~~~~~~~~

.. autoclass:: CiscoIOS
   :members:
   :inherited-members:

CiscoASA
~~~~~~~~

.. autoclass:: CiscoASA
   :members:
   :inherited-members:

CiscoNXOS
~~~~~~~~~

.. autoclass:: CiscoNXOS
   :members:
   :inherited-members:

FujitsuSwitch
~~~~~~~~~~~~~

.. autoclass:: FujitsuSwitch
   :members:
   :inherited-members:

HPComware
~~~~~~~~~

.. autoclass:: HPComware
   :members:
   :inherited-members:

MikrotikRouterOS
~~~~~~~~~~~~~~~~

.. autoclass:: MikrotikRouterOS
   :members:
   :inherited-members:



