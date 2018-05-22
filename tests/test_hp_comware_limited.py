import asyncio
import logging
import unittest

import yaml

import netdev

logging.basicConfig(filename='unittest.log', level=logging.DEBUG)
config_path = 'config.yaml'


class TestComwareLimited(unittest.TestCase):
    @staticmethod
    def load_credits():
        with open(config_path, 'r') as conf:
            config = yaml.load(conf)
            with open(config['device_list'], 'r') as devs:
                devices = yaml.load(devs)
                params = [p for p in devices if p['device_type'] == 'hp_comware_limited']
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
                async with netdev.create(**dev) as hp:
                    out = await hp.send_command('display cur | i sysname')
                    self.assertIn("sysname", out)

        self.loop.run_until_complete(task())

    def test_show_several_commands(self):
        async def task():
            for dev in self.devices:
                async with netdev.create(**dev) as hp:
                    commands = ["dir", "display ver", "display cur", "display ssh server status"]
                    for cmd in commands:
                        out = await hp.send_command(cmd, strip_command=False)
                        self.assertIn(cmd, out)

        self.loop.run_until_complete(task())

    def test_config_set(self):
        async def task():
            for dev in self.devices:
                async with netdev.create(**dev) as hp:
                    commands = ["vlan 1", "quit"]
                    out = await hp.send_config_set(commands)
                    self.assertIn("vlan 1", out)
                    self.assertIn("quit", out)

        self.loop.run_until_complete(task())

    def test_base_prompt(self):
        async def task():
            for dev in self.devices:
                async with netdev.create(**dev) as hp:
                    out = await hp.send_command('display cur | i sysname')
                    self.assertIn(hp.base_prompt, out)

        self.loop.run_until_complete(task())

    def test_timeout(self):
        async def task():
            for dev in self.devices:
                with self.assertRaises(netdev.TimeoutError):
                    async with netdev.create(**dev, timeout=0.1) as hp:
                        await hp.send_command('display cur | i sysname')

        self.loop.run_until_complete(task())
