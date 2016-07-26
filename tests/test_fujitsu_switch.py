import asyncio
import logging
import unittest

import yaml

import netdev

logging.basicConfig(filename='tests/unittest.log', level=logging.DEBUG)
config_path = 'config.yaml'


class TestFujitsu(unittest.TestCase):
    @staticmethod
    def load_credits():
        with open(config_path, 'r') as conf:
            config = yaml.load(conf)
            with open(config['device_list'], 'r') as devs:
                devices = yaml.load(devs)
                params = [p for p in devices if p['device_type'] == 'fujitsu_switch']
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
                fuj = netdev.create(**dev)
                await fuj.connect()
                out = await fuj.send_command('show run | i snmp')
                self.assertIn("snmp", out)
                await fuj.disconnect()

        self.loop.run_until_complete(task())

    def test_show_several_commands(self):
        async def task():
            for dev in self.devices:
                fuj = netdev.create(**dev)
                await fuj.connect()
                commands = ["dir", "show ver", "show run", "show ssh"]
                for cmd in commands:
                    out = await fuj.send_command(cmd, strip_command=False)
                    self.assertIn(cmd, out)
                await fuj.disconnect()

        self.loop.run_until_complete(task())

    def test_config_set(self):
        async def task():
            for dev in self.devices:
                fuj = netdev.create(**dev)
                await fuj.connect()
                commands = ["vlan database", "exit"]
                out = await fuj.send_config_set(commands)
                self.assertIn("vlan database", out)
                self.assertIn("exit", out)
                await fuj.disconnect()

        self.loop.run_until_complete(task())

    def test_base_prompt(self):
        async def task():
            for dev in self.devices:
                fuj = netdev.create(**dev)
                await fuj.connect()
                out = await fuj.send_command("sh run | i 'switch '")
                self.assertIn(fuj.base_prompt, out)
                await fuj.disconnect()

        self.loop.run_until_complete(task())
