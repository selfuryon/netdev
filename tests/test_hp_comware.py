import asyncio
import logging
import unittest

import yaml

import netdev

logging.basicConfig(filename='tests/unittest.log', level=logging.DEBUG)
config_path = 'config.yaml'


class TestComware(unittest.TestCase):
    @staticmethod
    def load_credits():
        with open(config_path, 'r') as conf:
            config = yaml.load(conf)
            with open(config['device_list'], 'r') as devs:
                devices = yaml.load(devs)
                params = [p for p in devices if p['device_type'] == 'hp_comware']
                return params

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        self.loop.set_debug(False)
        asyncio.set_event_loop(self.loop)
        self.devices = self.load_credits()
        self.assertFalse(len(self.devices) == 0)

    def test_show_sysname(self):
        async def task():
            for dev in self.devices:
                hp = netdev.create(**dev)
                await hp.connect()
                out = await hp.send_command('display cur | i sysname')
                self.assertIn("sysname", out)
                await hp.disconnect()

        self.loop.run_until_complete(task())

    def test_show_several_commands(self):
        async def task():
            for dev in self.devices:
                hp = netdev.create(**dev)
                await hp.connect()
                commands = ["dir", "display ver", "display cur", "display ssh server status"]
                for cmd in commands:
                    out = await hp.send_command(cmd, strip_command=False)
                    self.assertIn(cmd, out)
                await hp.disconnect()

        self.loop.run_until_complete(task())

    def test_config_set(self):
        async def task():
            for dev in self.devices:
                hp = netdev.create(**dev)
                await hp.connect()
                commands = ["vlan 1", "quit"]
                out = await hp.send_config_set(commands)
                self.assertIn("vlan 1", out)
                self.assertIn("quit", out)
                await hp.disconnect()

        self.loop.run_until_complete(task())

    def test_base_prompt(self):
        async def task():
            for dev in self.devices:
                hp = netdev.create(**dev)
                await hp.connect()
                out = await hp.send_command('display cur | i sysname')
                self.assertIn(hp.base_prompt, out)
                await hp.disconnect()

        self.loop.run_until_complete(task())
