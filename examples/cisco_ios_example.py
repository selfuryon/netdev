import asyncio
import logging

import yaml

import netdev

config_path = 'config.yaml'

logging.basicConfig(level=logging.DEBUG)


async def task(param):
    ios = netdev.connect(**param)
    await ios.connect()
    out = await ios.send_command("show ssh")
    print(out)
    commands = ["line console 0", "exit"]
    out = await ios.send_config_set(commands)
    print(out)
    out = await ios.send_command("show run")
    print(out)
    await ios.disconnect()


async def run():
    config = yaml.load(open(config_path, 'r'))
    devices = yaml.load(open(config['device_list'], 'r'))
    params = [p for p in devices if p['device_type'] == 'cisco_ios']
    tasks = []
    for param in params:
        tasks.append(task(param))
    await asyncio.wait(tasks)


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
