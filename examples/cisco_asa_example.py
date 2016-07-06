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
    await asa.send_command("changeto context inet")
    print(asa.current_context)
    await asa.send_command("changeto context wan")
    print(asa.current_context)
    await asa.send_command("changeto system")
    print(asa.current_context)
    await asa.send_command("changeto context admin")
    print(asa.current_context)


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
