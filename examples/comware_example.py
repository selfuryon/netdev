import asyncio
import logging

import yaml

import netdev

creds = 'device_credits.yaml'

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


async def task(param):
    hp = netdev.connect(**param)
    await hp.connect()
    commands = ["interface Vlan-interface1", "quit"]
    out = await hp.send_config_set(commands)
    print(out)


async def run():
    devices = yaml.load(open(creds, 'r'))
    params = [p for p in devices if p['device_type'] == 'hp_comware']
    tasks = []
    for param in params:
        tasks.append(task(param))
    await asyncio.wait(tasks)


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
