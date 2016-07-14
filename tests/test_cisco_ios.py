import asyncio
import logging
import unittest

import yaml

import netdev

logging.basicConfig(filename="unittest.log", level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class TestCisco(unittest.TestCase):
    @staticmethod
    def load_credits():
        config_path = 'config.yaml'
        config = yaml.load(open(config_path, 'r'))
        devices = yaml.load(open(config['device_credentials'], 'r'))
        params = [p for p in devices if p['device_type'] == 'cisco_ios']
        return params

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        self.loop.set_debug(False)
        asyncio.set_event_loop(self.loop)

    def test_show_run_hostname(self):
        params = self.load_credits()

        async def task():
            for param in params:
                ios = netdev.connect(**param)
                await ios.connect()
                out = await ios.send_command('show run | i hostname')
                self.assertIn("hostname", out)
                await ios.disconnect()

        self.loop.run_until_complete(task())

    def test_show_several_commands(self):
        params = self.load_credits()

        async def task():
            for param in params:
                ios = netdev.connect(**param)
                await ios.connect()
                commands = ["dir", "show ver", "show run", "show ssh"]
                for cmd in commands:
                    out = await ios.send_command(cmd, strip_command=False)
                    self.assertIn(cmd, out)
                await ios.disconnect()

        self.loop.run_until_complete(task())

    def test_config_set(self):
        params = self.load_credits()

        async def task():
            for param in params:
                ios = netdev.connect(**param)
                await ios.connect()
                commands = ["line con 0", "exit"]
                out = await ios.send_config_set(commands)
                self.assertIn("line con 0", out)
                self.assertIn("exit", out)
                await ios.disconnect()

        self.loop.run_until_complete(task())

    def test_base_prompt(self):
        params = self.load_credits()

        async def task():
            for param in params:
                ios = netdev.connect(**param)
                await ios.connect()
                out = await ios.send_command('sh run | i hostname')
                self.assertIn(ios.base_prompt, out)
                await ios.disconnect()

        self.loop.run_until_complete(task())
