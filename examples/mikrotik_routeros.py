import asyncio
import logging

import yaml

import netdev

config_path = 'config.yaml'

logging.basicConfig(level=logging.INFO)
netdev.logger.setLevel(logging.DEBUG)


async def task(param):
    async with netdev.create(**param) as routeros:
        # Testing sending simple command
        commands = ['/ip address', 'print', '/']
        for cmd in commands:
            print(await routeros.send_command(cmd))

        # Testing sending configuration set
        out = await routeros.send_config_set(commands)
        print(out)


async def run():
    config = yaml.load(open(config_path, 'r'))
    devices = yaml.load(open(config['device_list'], 'r'))
    tasks = [task(dev) for dev in devices if dev['device_type'] == 'mikrotik_routeros']
    await asyncio.wait(tasks)


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
