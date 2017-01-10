import asyncio
import logging

import yaml

import netdev

config_path = 'config.yaml'

logging.basicConfig(level=logging.INFO)
netdev.logger.setLevel(logging.DEBUG)


async def task(param):
    async with netdev.create(**param) as junos:
        # Testing sending simple command
        out = await junos.send_command("show version")
        print(out)
        # Testing sending configuration set
        commands = ["edit system", "edit login"]
        out = await junos.send_config_set(commands, with_commit=True)
        print(out)
        # Testing sending simple command with long output
        out = await junos.send_command("show config")
        print(out)
        # Testing interactive dialog
        commands = ["set system login message 123", "delete system login message 123"]
        out = await junos.send_config_set(commands, with_commit=False, exit_config_mode=False)
        out += await junos.send_command("exit", pattern=r'Exit with uncommitted changes\?', strip_command=False)
        out += await junos.send_command("no", strip_command=False)
        out += await junos.send_command("rollback 0", strip_command=False)
        out += await junos.send_command("exit configuration-mode", strip_command=False)
        print(out)


async def run():
    config = yaml.load(open(config_path, 'r'))
    devices = yaml.load(open(config['device_list'], 'r'))
    tasks = [task(dev) for dev in devices if dev['device_type'] == 'juniper_junos']
    await asyncio.wait(tasks)


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
