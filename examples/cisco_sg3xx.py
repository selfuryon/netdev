#!/usr/bin/env python3

# Import Python library
import asyncio, netdev

# Coroutine used for the tasks
async def task(param):

    # Create an object for the devices and open SSH connections
    async with netdev.create(**param) as ios:

        # Testing sending simple command
        
        # Command to send
        cmd = "show clock"

        # Sending command
        output = await ios.send_command(cmd)

        # Display the output
        print(output)

# Main coroutine
async def main():

    # Parameters of the network device
    my_device = {   'username' : 'LOGIN',
                    'password' : 'PASSWORD',
                    'host': 'IP_ADDRESS',
                    'device_type': 'cisco_sg3xx',
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
    .14:07:35 J  Aug 28 2020
    Time source is sntp
    Time from Browser is disabled
    ********************************************************************************

    '''