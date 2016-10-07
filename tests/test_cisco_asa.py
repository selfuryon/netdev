import asyncio
import logging
import unittest

import yaml

import netdev

logging.basicConfig(filename='tests/unittest.log', level=logging.DEBUG)
config_path = 'config.yaml'


class TestASA(unittest.TestCase):
    @staticmethod
    def load_credits():
        with open(config_path, 'r') as conf:
            config = yaml.load(conf)
            with open(config['device_list'], 'r') as devs:
                devices = yaml.load(devs)
                params = [p for p in devices if p['device_type'] == 'cisco_asa']
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
                async with netdev.create(**dev) as asa:
                    out = await asa.send_command('show run | i hostname')
                    self.assertIn("hostname", out)

        self.loop.run_until_complete(task())

    def test_show_several_commands(self):
        async def task():
            for dev in self.devices:
                async with netdev.create(**dev) as asa:
                    commands = ["show ver", "show run", "show ssh"]
                    for cmd in commands:
                        out = await asa.send_command(cmd, strip_command=False)
                        self.assertIn(cmd, out)

        self.loop.run_until_complete(task())

    def test_config_set(self):
        async def task():
            for dev in self.devices:
                async with netdev.create(**dev) as asa:
                    commands = ["interface Management0/0", "exit"]
                    out = await asa.send_config_set(commands)
                    self.assertIn("interface Management0/0", out)
                    self.assertIn("exit", out)

        self.loop.run_until_complete(task())

    def test_current_context(self):
        async def task():
            for dev in self.devices:
                async with netdev.create(**dev) as asa:
                    if asa.multiple_mode:
                        await asa.send_command('changeto system')
                        self.assertIn('system', asa.current_context)
                        out = await asa.send_command('sh run | i ^context')
                        contexts = out.splitlines()
                        for ctx in contexts:
                            out = await asa.send_command('changeto {}'.format(ctx))
                            self.assertIn(ctx.split()[1], asa.current_context)
                    else:
                        self.assertIn('system', asa.current_context)

        self.loop.run_until_complete(task())
