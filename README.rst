Netdev
******

Asynchronous multi-vendor library for interacting with network devices

Inspired by netmiko

Requires:
---------
* asyncio
* AsyncSSH
* Python 3.5
* pyYAML
  
 
Supports: 
---------
* Cisco IOS 
* Cisco IOS-XE 
* Cisco ASA
* Cisco NX-OS 
* HP Comware
* Fujitsu Blade Switches
* Mikrotik RouterOS

Examples:
---------
Example of interacting with cisco IOS devices:

.. code-block:: python

    import asyncio
    import netdev

    async def task(param):
        async with netdev.create(**param) as ios:
            out = await ios.send_command("show ssh")
            print(out)
            commands = ["line console 0", "exit"]
            out = await ios.send_config_set(commands)
            print(out)
            out = await ios.send_command("show run")
            print(out)


    async def run():
        dev1 = { 'username' : 'user,
                 'password' : 'pass',
                 'device_type': 'cisco_ios',
                 'host': 'ip address',
        }
        dev2 = { 'username' : 'user,
                 'password' : 'pass',
                 'device_type': 'cisco_ios',
                 'host': 'ip address',
        }
        devices = [dev1, dev2]
        for dev in devices:
            tasks.append(task(dev))
        await asyncio.wait(tasks)


    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())


 
