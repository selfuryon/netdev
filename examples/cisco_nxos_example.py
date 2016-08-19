import asyncio
import logging

import yaml

import netdev

config_path = 'config.yaml'

logging.basicConfig(level=logging.DEBUG)
netdev.logger.setLevel(logging.DEBUG)


async def task(param):
    nxos = netdev.create(**param)
    await nxos.connect()
    out = await nxos.send_command('show run', strip_command=True)
    print(out)
    await nxos.disconnect()


async def run():
    config = yaml.load(open(config_path, 'r'))
    devices = yaml.load(open(config['device_list'], 'r'))
    params = [p for p in devices if p['device_type'] == 'cisco_nxos']
    tasks = []
    for param in params:
        tasks.append(task(param))
    await asyncio.wait(tasks)


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
