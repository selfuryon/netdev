import asyncio
import logging
import unittest

import yaml

import netdev

logging.basicConfig(filename="unittest.log", level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def load_credits():
    config_path = 'config.yaml'
    config = yaml.load(open(config_path, 'r'))
    devices = yaml.load(open(config['device_credentials'], 'r'))
    params = [p for p in devices if p['device_type'] == 'fujitsu_switch']
    return params


class TestCisco(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        self.loop.set_debug(False)
        asyncio.set_event_loop(self.loop)

    def test_show_hostname(self):
        params = load_credits()

        async def task(param):
            fuj = netdev.connect(**param)
            await fuj.connect()
            out = await fuj.send_command('show run | i snmp')
            self.assertIn("snmp", out)

        async def run():
            tasks = []
            for param in params:
                tasks.append(task(param))
            await asyncio.wait(tasks)

        self.loop.run_until_complete(run())

    def test_show_several_commands(self):
        params = load_credits()

        async def task(param):
            fuj = netdev.connect(**param)
            await fuj.connect()
            commands = ["dir", "show ver", "show run", "show ssh"]
            for cmd in commands:
                out = await fuj.send_command(cmd, strip_command=False)
                self.assertIn(cmd, out)

        async def run():
            tasks = []
            for param in params:
                tasks.append(task(param))
            await asyncio.wait(tasks)

        self.loop.run_until_complete(run())

    def test_config_set(self):
        params = load_credits()

        async def task(param):
            fuj = netdev.connect(**param)
            await fuj.connect()
            commands = ["vlan database", "exit"]
            out = await fuj.send_config_set(commands)
            self.assertIn("vlan database", out)
            self.assertIn("exit", out)

        async def run():
            tasks = []
            for param in params:
                tasks.append(task(param))
            await asyncio.wait(tasks)

        self.loop.run_until_complete(run())
