import asyncio
import logging
import unittest
import yaml
import netdev

logging.basicConfig(filename='unittest.log', level=logging.DEBUG)
config_path = 'config.yaml'

class TestHW1000(unittest.TestCase):
    @staticmethod
    def load_credits():
        with open(config_path, 'r') as conf:
            config = yaml.load(conf)
            with open(config['device_list'], 'r') as devs:
                devices = yaml.load(devs)
                params = [p for p in devices if p['device_type'] == 'hw1000']
                return params

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        self.loop.set_debug(False)
        asyncio.set_event_loop(self.loop)
        self.devices = self.load_credits()
        self.assertFalse(len(self.devices) == 0)

    def test_simple_command(self):
        async def task():
            for dev in self.devices:
                async with netdev.create(**dev) as hw:
                    out = await hw.send_command("inet show snmp")
                    self.assertIn('SNMP',out)
        self.loop.run_until_complete(task())

    def test_long_command(self):
        async def task():
            for dev in self.devices:
                async with netdev.create(**dev) as hw:
                    out = await hw.send_command("inet show interface")
                    out_len=(len(out.split('\n')))
                    self.assertGreater(out_len,10)
        self.loop.run_until_complete(task())

    def test_linux_mode(self):
        async def task():
            for dev in self.devices:
                async with netdev.create(**dev) as hw:
                    out = await hw.enter_shell_mode()
                    out = await hw.send_command("id")
                    self.assertIn('uid=0(root)',out)
        self.loop.run_until_complete(task())

    def test_linux_mode_indepotence(self):
        async def task():
            for dev in self.devices:
                async with netdev.create(**dev) as hw:
                    out = await hw.enter_shell_mode()
                    out = await hw.enter_shell_mode()
                    out = await hw.send_command("id")
                    self.assertIn('uid=0(root)',out)
        self.loop.run_until_complete(task())
