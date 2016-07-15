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
                fuj = netdev.connect(**dev)
                await fuj.connect()
                out = await fuj.send_command('show run | i snmp')
                self.assertIn("snmp", out)
                await fuj.disconnect()

        self.loop.run_until_complete(task())

    def test_show_several_commands(self):
        async def task():
            for dev in self.devices:
                fuj = netdev.connect(**dev)
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
                fuj = netdev.connect(**dev)
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
                fuj = netdev.connect(**dev)
                await fuj.connect()
                out = await fuj.send_command("sh run | i 'switch '")
                self.assertIn(fuj.base_prompt, out)
                await fuj.disconnect()

        self.loop.run_until_complete(task())
