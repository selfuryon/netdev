import asyncio
import logging

import yaml

import netdev

config_path = 'config.yaml'

logging.basicConfig(level=logging.INFO)
netdev.logger.setLevel(logging.DEBUG)


async def task(param):
    async with netdev.create(**param) as hp:
        # Testing sending simple command
        out = await hp.send_command('display ver')
        print(out)
        # Testing sending configuration set
        commands = ["Vlan 1", "quit"]
        out = await hp.send_config_set(commands)
        print(out)
        # Testing sending simple command with long output
        out = await hp.send_command('display cur')
        print(out)


async def run():
    config = yaml.load(open(config_path, 'r'))
    devices = yaml.load(open(config['device_list'], 'r'))
    tasks = [task(dev) for dev in devices if dev['device_type'] == 'hp_comware']
    await asyncio.wait(tasks)


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
