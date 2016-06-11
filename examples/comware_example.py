import asyncio
import logging

import yaml

import netdev

creds = "hp_comware_credits.yaml"

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


async def task(param):
    hp = netdev.connect(**param)
    await hp.connect()
    commands = ["interface Vlan-interface1", "quit"]
    out = await hp.send_config_set(commands)
    print(out)


async def run():
    params = yaml.load(open(creds, 'r'))
    tasks = []
    for param in params:
        tasks.append(task(param))
    await asyncio.wait(tasks)


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
