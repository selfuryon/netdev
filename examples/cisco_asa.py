import asyncio
import logging

import yaml

import netdev

config_path = 'config.yaml'

logging.basicConfig(level=logging.INFO)
netdev.logger.setLevel(logging.DEBUG)


async def task(param):
    async with netdev.create(**param) as asa:
        # Testing sending simple command
        out = await asa.send_command('show run')
        print(out)
        # Testing interactive dialog
        out = await asa.send_command("copy r scp:", pattern=r'\[running-config\]\?', strip_command=False)
        out += await asa.send_command("\n", pattern=r'\[\]\?', strip_command=False)
        out += await asa.send_command("\n", strip_command=False)
        print(out)


async def run():
    config = yaml.safe_load(open(config_path, 'r'))
    devices = yaml.safe_load(open(config['device_list'], 'r'))
    tasks = [task(dev) for dev in devices if dev['device_type'] == 'cisco_asa']
    await asyncio.wait(tasks)


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
