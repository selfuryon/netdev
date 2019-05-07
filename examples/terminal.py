import asyncio
import logging

import yaml

import netdev

config_path = 'config.yaml'

logging.basicConfig(level=logging.INFO)
netdev.logger.setLevel(logging.DEBUG)


async def task(param):
    async with netdev.create(**param) as term:
        # Testing sending simple command
        out = await term.send_command('ls -al', strip_command=True)
        print(out)
        out = await term.send_command('pwd', strip_command=True)
        print(out)
        out = await term.send_command('echo test', strip_command=True)
        print(out)


async def run():
    config = yaml.safe_load(open(config_path, 'r'))
    devices = yaml.safe_load(open(config['device_list'], 'r'))
    tasks = [task(dev) for dev in devices if dev['device_type'] == 'terminal']
    await asyncio.wait(tasks)


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
