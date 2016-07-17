.. module:: netdev

.. _API:

API Documentation
*****************

Overview
========

Netdev is an asynchronous library for working with network devices. For each vendor you should use separate class for
working. For this purpose are used Factory method :func:`connect`

.. autofunction:: connect

.. autoclass:: netdev.netdev_base.NetDev
   :members:
   :special-members: __init__

Hello!
