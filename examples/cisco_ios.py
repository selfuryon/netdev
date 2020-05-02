import asyncio
import logging
import os
import sys

import yaml

import netdev

logging.basicConfig(level=logging.WARNING)
netdev.logger.setLevel(logging.DEBUG)
# netdev.logger.getChild("Layer").setLevel(logging.DEBUG)
# netdev.logger.getChild("LayerManager").setLevel(logging.DEBUG)


async def task(param):
    async with netdev.create(**param) as ios:
        # Testing sending simple command
        out = await ios.send_command("show ver")
        print(out)
        # Testing sending configuration set
        #commands = ["line console 0", "exit"]
        # out = await ios.send_config_set(commands)
        # print(out)
        # Testing sending simple command with long output
        # out = await ios.send_command("show run")
        # print(out)
        # Testing interactive dialog
        # out = await ios.send_command(
        #    "conf", pattern=r"\[terminal\]\?", strip_command=False
        # )
        # out += await ios.send_command("term", strip_command=False)
        # out += await ios.send_command("exit", strip_command=False, strip_prompt=False)
        # print(out)


async def run():
    devices_path = os.environ['EXAMPLE_DEVICES']
    devices = yaml.safe_load(open(devices_path, "r"))
    tasks = [task(dev) for dev in devices if dev["device_type"] == "cisco_ios"]
    await asyncio.wait(tasks)


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
