import asyncio
import logging
import unittest

import yaml

import netdev

logging.basicConfig(filename='tests/unittest.log', level=logging.DEBUG)
config_path = 'config.yaml'


class TestIOS(unittest.TestCase):
    @staticmethod
    def load_credits():
        with open(config_path, 'r') as conf:
            config = yaml.load(conf)
            with open(config['device_list'], 'r') as devs:
                devices = yaml.load(devs)
                params = [p for p in devices if p['device_type'] == 'cisco_ios']
                return params

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        self.loop.set_debug(False)
        asyncio.set_event_loop(self.loop)
        self.devices = self.load_credits()
        self.assertFalse(len(self.devices) == 0)

    def test_show_run_hostname(self):
        async def task():
            for dev in self.devices:
                ios = netdev.create(**dev)
                await ios.connect()
                out = await ios.send_command('show run | i hostname')
                self.assertIn("hostname", out)
                await ios.disconnect()

        self.loop.run_until_complete(task())

    def test_show_several_commands(self):
        async def task():
            for dev in self.devices:
                ios = netdev.create(**dev)
                await ios.connect()
                commands = ["dir", "show ver", "show run", "show ssh"]
                for cmd in commands:
                    out = await ios.send_command(cmd, strip_command=False)
                    self.assertIn(cmd, out)
                await ios.disconnect()

        self.loop.run_until_complete(task())

    def test_config_set(self):
        async def task():
            for dev in self.devices:
                ios = netdev.create(**dev)
                await ios.connect()
                commands = ["line con 0", "exit"]
                out = await ios.send_config_set(commands)
                self.assertIn("line con 0", out)
                self.assertIn("exit", out)
                await ios.disconnect()

        self.loop.run_until_complete(task())

    def test_base_prompt(self):
        async def task():
            for dev in self.devices:
                ios = netdev.create(**dev)
                await ios.connect()
                out = await ios.send_command('sh run | i hostname')
                self.assertIn(ios.base_prompt, out)
                await ios.disconnect()

        self.loop.run_until_complete(task())
