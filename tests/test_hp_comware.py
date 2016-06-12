import asyncio
import logging
import unittest

import yaml

import netdev

logging.basicConfig(filename="unittest.log", level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class TestCisco(unittest.TestCase):
    def load_credits(self):
        creds = 'device_credits.yaml'
        devices = yaml.load(open(creds, 'r'))
        params = [p for p in devices if p['device_type'] == 'hp_comware']
        return params

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        self.loop.set_debug(False)
        asyncio.set_event_loop(self.loop)

    def test_show_hostname(self):
        params = self.load_credits()

        async def task(param):
            hp = netdev.connect(**param)
            await hp.connect()
            out = await hp.send_command('display cur | i sysname')
            self.assertIn("sysname", out)

        async def run():
            tasks = []
            for param in params:
                tasks.append(task(param))
            await asyncio.wait(tasks)

        self.loop.run_until_complete(run())

    def test_show_several_commands(self):
        params = self.load_credits()

        async def task(param):
            hp = netdev.connect(**param)
            await hp.connect()
            commands = ["dir", "display ver", "display run", "display ssh server status"]
            for cmd in commands:
                out = await hp.send_command(cmd)

        async def run():
            tasks = []
            for param in params:
                tasks.append(task(param))
            await asyncio.wait(tasks)

        self.loop.run_until_complete(run())

    def test_config_set(self):
        params = self.load_credits()

        async def task(param):
            hp = netdev.connect(**param)
            await hp.connect()
            commands = ["interface Vlan-interface1", "quit"]
            out = await hp.send_config_set(commands)
            self.assertIn("interface Vlan-interface1", out)
            self.assertIn("quit", out)

        async def run():
            tasks = []
            for param in params:
                tasks.append(task(param))
            await asyncio.wait(tasks)

        self.loop.run_until_complete(run())
