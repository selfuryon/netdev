import asyncio
import logging
import unittest

import yaml

import netdev

logging.basicConfig(filename='unittest.log', level=logging.DEBUG)
config_path = 'config.yaml'


class TestIOSXR(unittest.TestCase):
    @staticmethod
    def load_credits():
        with open(config_path, 'r') as conf:
            config = yaml.load(conf)
            with open(config['device_list'], 'r') as devs:
                devices = yaml.load(devs)
                params = [p for p in devices if p['device_type'] == 'cisco_ios_xr']
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
                async with netdev.create(**dev) as iosxr:
                    out = await iosxr.send_command('show run | i hostname')
                    self.assertIn("hostname", out)

        self.loop.run_until_complete(task())

    def test_timeout(self):
        async def task():
            for dev in self.devices:
                with self.assertRaises(netdev.TimeoutError):
                    async with netdev.create(**dev, timeout=0.1) as iosxr:
                        await iosxr.send_command('show run | i hostname')

        self.loop.run_until_complete(task())

    def test_show_several_commands(self):
        async def task():
            for dev in self.devices:
                async with netdev.create(**dev) as iosxr:
                    commands = ["dir", "show ver", "show run", "show ssh"]
                    for cmd in commands:
                        out = await iosxr.send_command(cmd, strip_command=False)
                        self.assertIn(cmd, out)

        self.loop.run_until_complete(task())

    def test_config_set(self):
        async def task():
            for dev in self.devices:
                async with netdev.create(**dev) as iosxr:
                    commands = ["line con 0", "exit"]
                    out = await iosxr.send_config_set(commands)
                    self.assertIn("line con 0", out)
                    self.assertIn("exit", out)

        self.loop.run_until_complete(task())

    def test_interactive_commands(self):
        async def task():
            for dev in self.devices:
                async with netdev.create(**dev) as ios:
                    out = await ios.send_command("conf", strip_command=False)
                    out += await ios.send_command("hostname test", strip_command=False)
                    out += await ios.send_command("exit", pattern=r'Uncommitted changes found', strip_command=False)
                    out += await ios.send_command("no", strip_command=False)
                    self.assertIn('commit them before exiting', out)

        self.loop.run_until_complete(task())

    def test_exit_without_commit(self):
        async def task():
            for dev in self.devices:
                async with netdev.create(**dev) as ios:
                    commands = ["interface GigabitEthernet 0/0/0/0", "service-policy input 1"]
                    out = await ios.send_config_set(commands, with_commit=False)
                    self.assertIn('Uncommitted changes found', out)

        self.loop.run_until_complete(task())

    def test_errors_in_commit(self):
        async def task():
            for dev in self.devices:
                with self.assertRaises(netdev.CommitError):
                    async with netdev.create(**dev) as ios:
                        commands = ["interface GigabitEthernet 0/0/0/0", "service-policy input 1"]
                        await ios.send_config_set(commands)

        self.loop.run_until_complete(task())
