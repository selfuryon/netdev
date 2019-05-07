---
name: Bug Report
about: Report a bug in Netdev library
---

**Describe the bug**

A clear and concise description of what the bug is.

**General Information**

 - OS [e.g. Windows 10]
 - Netdev version [e.g. 0.9.0]
 - Device OS [e.g. Cisco IOS XE 3.4.6]

**Debug information**

I usually need a debug information for understanding what exactly happened. You can get it by using this code:

```python
import netdev
import logging

logging.basicConfig(level=logging.INFO)
netdev.logger.setLevel(logging.DEBUG)
```

**Additional context**

Add any other context about the problem here.
