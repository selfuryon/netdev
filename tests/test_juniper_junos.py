import asyncio
import logging
import unittest

import yaml

import netdev

logging.basicConfig(filename='unittest.log', level=logging.DEBUG)
config_path = 'config.yaml'


class TestJunOS(unittest.TestCase):
    @staticmethod
    def load_credits():
        with open(config_path, 'r') as conf:
            config = yaml.load(conf)
            with open(config['device_list'], 'r') as devs:
                devices = yaml.load(devs)
                params = [p for p in devices if p['device_type'] == 'juniper_junos']
                return params

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        self.loop.set_debug(False)
        asyncio.set_event_loop(self.loop)
        self.devices = self.load_credits()
        self.assertFalse(len(self.devices) == 0)

    def test_show_system_hostname(self):
        async def task():
            for dev in self.devices:
                async with netdev.create(**dev) as junos:
                    out = await junos.send_command('show configuration system host-name')
                    self.assertIn("host-name", out)

        self.loop.run_until_complete(task())

    def test_timeout(self):
        async def task():
            for dev in self.devices:
                with self.assertRaises(netdev.TimeoutError):
                    async with netdev.create(**dev, timeout=0.1) as junos:
                        await junos.send_command('show configuration system host-name')

        self.loop.run_until_complete(task())

    def test_show_several_commands(self):
        async def task():
            for dev in self.devices:
                async with netdev.create(**dev) as junos:
                    commands = ["show ver", "show conf", "show chassis firmware"]
                    for cmd in commands:
                        out = await junos.send_command(cmd, strip_command=False)
                        self.assertIn(cmd, out)

        self.loop.run_until_complete(task())

    def test_config_set(self):
        async def task():
            for dev in self.devices:
                async with netdev.create(**dev) as junos:
                    commands = ["edit system", "edit login"]
                    out = await junos.send_config_set(commands, with_commit=False)
                    self.assertIn("edit system", out)
                    self.assertIn("edit login", out)

        self.loop.run_until_complete(task())

    def test_base_prompt(self):
        async def task():
            for dev in self.devices:
                async with netdev.create(**dev) as junos:
                    out = await junos.send_command('show configuration system host-name')
                    self.assertIn(junos.base_prompt, out)

        self.loop.run_until_complete(task())

    def test_interactive_commands(self):
        async def task():
            for dev in self.devices:
                async with netdev.create(**dev) as junos:
                    commands = ["set system login message 123", "delete system login message 123"]
                    out = await junos.send_config_set(commands, with_commit=False, exit_config_mode=False)
                    out += await junos.send_command("exit", pattern=r'Exit with uncommitted changes\?',
                                                    strip_command=False)
                    out += await junos.send_command("no", strip_command=False)
                    out += await junos.send_command("rollback 0", strip_command=False)
                    out += await junos.send_command("exit configuration-mode", strip_command=False)
                    self.assertIn('load complete', out)

        self.loop.run_until_complete(task())
