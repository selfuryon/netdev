import asyncio
import logging

import yaml

import netdev

config_path = 'config.yaml'

logging.basicConfig(level=logging.INFO)
netdev.logger.setLevel(logging.DEBUG)


async def task(param):
    async with netdev.create(**param) as arista:
        # Testing sending simple command
        out = await arista.send_command('show run', strip_command=True)
        print(out)
        # Testing sending configuration set
        commands = ["vlan 1", "exit"]
        out = await arista.send_config_set(commands)
        print(out)


async def run():
    config = yaml.safe_load(open(config_path, 'r'))
    devices = yaml.safe_load(open(config['device_list'], 'r'))
    tasks = [task(dev) for dev in devices if dev['device_type'] == 'arista_eos']
    await asyncio.wait(tasks)


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
