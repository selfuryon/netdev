import asyncio
import logging

import yaml

import netdev

config_path = 'config.yaml'

logging.basicConfig(level=logging.INFO)
netdev.logger.setLevel(logging.DEBUG)


async def task(param):
    async with netdev.create(**param) as iosxr:
        # Testing sending simple command
        out = await iosxr.send_command("show ver")
        print(out)
        # Testing sending simple command with long output
        out = await iosxr.send_command("show run")
        print(out)
        # Testing sending configuration set
        commands = ["interface loopback 0", "description TEST LOOPBACK"]
        out = await iosxr.send_config_set(commands, with_commit=True)
        print(out)
        # Testing failed commit
        commands = ["interface GigabitEthernet 0/0/0/0", "service-policy input 1"]
        out = await iosxr.send_config_set(commands, with_commit=False)
        print(out)
        try:
            commands = ["interface GigabitEthernet 0/0/0/0", "service-policy input 2"]
            await iosxr.send_config_set(commands)
        except netdev.CommitError:
            print("Commit Error")


async def run():
    config = yaml.load(open(config_path, 'r'))
    devices = yaml.load(open(config['device_list'], 'r'))
    tasks = [task(dev) for dev in devices if dev['device_type'] == 'cisco_ios_xr']
    await asyncio.gather(*tasks)


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
