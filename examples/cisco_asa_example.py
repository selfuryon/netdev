import asyncio
import logging

import yaml

import netdev

config_path = 'config.yaml'

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


async def task(param):
    asa = netdev.connect(**param)
    await asa.connect()
    print(asa.current_context)
    out = await asa.send_command('show run | i hostname')
    print(out)
    commands = ["policy-map global_policy", "exit"]
    out = await asa.send_config_set(commands)
    print(out)
    await asa.disconnect()


async def run():
    config = yaml.load(open(config_path, 'r'))
    devices = yaml.load(open(config['device_credentials'], 'r'))
    params = [p for p in devices if p['device_type'] == 'cisco_asa']
    tasks = []
    for param in params:
        tasks.append(task(param))
    await asyncio.wait(tasks)


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
