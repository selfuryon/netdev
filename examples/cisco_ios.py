import asyncio
import logging

import yaml

import netdev

config_path = "config.yaml"

logging.basicConfig(level=logging.INFO)
netdev.logger.setLevel(logging.DEBUG)


async def task(param):
    async with netdev.create(**param) as ios:
        # Testing sending simple command
        out = await ios.send_command("show ver")
        print(out)
        # Testing sending configuration set
        commands = ["line console 0", "exit"]
        out = await ios.send_config_set(commands)
        print(out)
        # Testing sending simple command with long output
        out = await ios.send_command("show run")
        print(out)
        # Testing interactive dialog
        out = await ios.send_command(
            "conf", pattern=r"\[terminal\]\?", strip_command=False
        )
        out += await ios.send_command("term", strip_command=False)
        out += await ios.send_command("exit", strip_command=False, strip_prompt=False)
        print(out)


async def run():
    config = yaml.safe_load(open(config_path, "r"))
    devices = yaml.safe_load(open(config["device_list"], "r"))
    tasks = [task(dev) for dev in devices if dev["device_type"] == "cisco_ios"]
    await asyncio.wait(tasks)


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
