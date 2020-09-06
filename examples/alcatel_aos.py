#!/usr/bin/env python3

# Import Python library
import asyncio, netdev

# Coroutine used for the tasks
async def task(param):

    # Create an object for the devices and open SSH connections
    async with netdev.create(**param) as device:

        # Testing sending simple command
        
        # Command to send
        cmd = "show system"

        # Sending command
        output = await device.send_command(cmd)

        # Display the output
        print(output)

        # Display separator
        print("*" * 80)

        # Testing sending configuration set

        # Commands to send
        commands = ["vlan 3000", "no vlan 3001"]

        # Sending command
        output = await device.send_config_set(commands)

        # Display the output
        print(output)


# Main coroutine
async def main():

    # Parameters of the network device
    my_device = {   'username' : 'LOGIN',
                    'password' : 'PASSWORD',
                    'host': 'IP_ADDRESS',
                    'device_type': 'alcatel_aos',
    }

    # List of devices
    devices = [my_device]
    
    # List of tasks
    my_tasks = [task(dev) for dev in devices]
    
    # Starting the coroutine of the tasks
    await asyncio.wait(my_tasks)


# Main function call
if __name__ == '__main__':

    # Run the main coroutine
    asyncio.run(main())

    '''
    Result:
    ********************************************************************************
    System:
    Description:  Alcatel-Lucent Enterprise OS6860E-48 8.4.1.141.R03 GA, December 07, 2017.,
    Object ID:    1.3.6.1.4.1.6486.801.1.1.2.1.11.1.7,
    Up Time:      5 days 5 hours 3 minutes and 56 seconds,
    Contact:      Alcatel-Lucent, http://enterprise.alcatel-lucent.com,
    Name:         switch01,
    Location:     Somewhere nearby,
    Services:     78,
    Date & Time:  SAT AUG 29 2020 18:48:53 (CEST)
    Flash Space:
        Primary CMM:
        Available (bytes):  933896192,
        Comments         :  None

    ********************************************************************************
    vlan 3000

    switch01 ==> no vlan 3001

    switch01 ==>

    ********************************************************************************

    '''