import asyncio

import yaml

import netdev

import logging

config_path = 'config.yaml'

logging.basicConfig(level=logging.WARN, format='%(asctime)s - %(levelname)s - %(message)s')


async def task(param):
    fuj = netdev.connect(**param)
    await fuj.connect()
    out = await fuj.send_config_set(['int bc5-SW01/0/1', 'exit'])
    print(out)


async def run():
    config = yaml.load(open(config_path, 'r'))
    devices = yaml.load(open(config['device_credentials'], 'r'))
    params = [p for p in devices if p['device_type'] == 'fujitsu_switch']
    tasks = []
    for param in params:
        tasks.append(task(param))
    await asyncio.wait(tasks)


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
