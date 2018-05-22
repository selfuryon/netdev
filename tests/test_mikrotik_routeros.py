import asyncio
import logging
import unittest

import yaml

import netdev

logging.basicConfig(filename='unittest.log', level=logging.DEBUG)
config_path = 'config.yaml'


class TestRouterOS(unittest.TestCase):
    @staticmethod
    def load_credits():
        with open(config_path, 'r') as conf:
            config = yaml.load(conf)
            with open(config['device_list'], 'r') as devs:
                devices = yaml.load(devs)
                params = [p for p in devices if p['device_type'] == 'mikrotik_routeros']
                return params

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        self.loop.set_debug(False)
        asyncio.set_event_loop(self.loop)
        self.devices = self.load_credits()
        self.assertFalse(len(self.devices) == 0)

    def test_show_system_identity(self):
        async def task():
            for dev in self.devices:
                async with netdev.create(**dev) as mik:
                    out = await mik.send_command('/system identity print')
                    self.assertIn(mik.base_prompt, out)

        self.loop.run_until_complete(task())

    def test_timeout(self):
        async def task():
            for dev in self.devices:
                with self.assertRaises(netdev.TimeoutError):
                    async with netdev.create(**dev, timeout=0.1) as mik:
                        await mik.send_command('/system identity print')

        self.loop.run_until_complete(task())

    def test_show_several_commands(self):
        async def task():
            for dev in self.devices:
                async with netdev.create(**dev) as mik:
                    commands = ["/ip address print", "/system package print", " /user print"]
                    for cmd in commands:
                        out = await mik.send_command(cmd, strip_command=False)
                        self.assertIn(cmd, out)

        self.loop.run_until_complete(task())
