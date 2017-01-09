import asyncio
import logging

import yaml

import netdev

config_path = 'config.yaml'

logging.basicConfig(level=logging.INFO)
netdev.logger.setLevel(logging.DEBUG)


async def task(param):
    async with netdev.create(**param) as ios:
        out = await ios.send_command("show ssh")
        print(out)
        commands = ["line console 0", "exit"]
        out = await ios.send_config_set(commands)
        print(out)
        out = await ios.send_command("show run")
        print(out)
        # Testing interactive dialog
        out = await ios.send_command("conf", pattern=r'\[terminal\]\?', strip_command=False)
        out += await ios.send_command("term", strip_command=False)
        out += await ios.send_command("exit", strip_command=False, strip_prompt=False)
        print(out)


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
