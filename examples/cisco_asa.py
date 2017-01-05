import asyncio
import logging

import yaml

import netdev

config_path = 'config.yaml'

logging.basicConfig(level=logging.DEBUG)
netdev.logger.setLevel(logging.DEBUG)

async def task(param):
    async with netdev.create(**param) as asa:
        print(asa.current_context)
        out = await asa.send_command('show run', strip_command=True)
        print(out)
        # Tests Interactive commands
        out = await asa.send_command("copy r scp:", pattern=r'\[running-config\]\?', strip_command=False)
        out += await asa.send_command("\n", pattern=r'\[\]\?', strip_command=False)
        out += await asa.send_command("\n", strip_command=False)
        print(out)


async def run():
    config = yaml.load(open(config_path, 'r'))
    devices = yaml.load(open(config['device_list'], 'r'))
    params = [p for p in devices if p['device_type'] == 'cisco_asa']
    tasks = []
    for param in params:
        tasks.append(task(param))
    await asyncio.wait(tasks)


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
