import asyncio
import logging
import unittest

import yaml

import netdev

logging.basicConfig(filename="unittest.log", level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class TestCisco(unittest.TestCase):
    def load_credits(self):
        creds = "cisco_asa_credits.yaml"
        params = yaml.load(open(creds, 'r'))
        return params

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        self.loop.set_debug(False)
        asyncio.set_event_loop(self.loop)

    def test_show_hostname(self):
        params = self.load_credits()

        async def task(param):
            asa = netdev.connect(**param)
            await asa.connect()
            out = await asa.send_command('show run | i hostname')
            self.assertIn("hostname", out)

        async def run():
            tasks = []
            for param in params:
                tasks.append(task(param))
            await asyncio.wait(tasks)

        self.loop.run_until_complete(run())

    def test_show_several_commands(self):
        params = self.load_credits()

        async def task(param):
            asa = netdev.connect(**param)
            await asa.connect()
            commands = ["dir", "show ver", "show run", "show ssh"]
            for cmd in commands:
                out = await asa.send_command(cmd)

        async def run():
            tasks = []
            for param in params:
                tasks.append(task(param))
            await asyncio.wait(tasks)

        self.loop.run_until_complete(run())

    def test_config_set(self):
        params = self.load_credits()

        async def task(param):
            asa = netdev.connect(**param)
            await asa.connect()
            commands = ["interface Management0/0", "exit"]
            out = await asa.send_config_set(commands)
            self.assertIn("interface Management0/0", out)
            self.assertIn("exit", out)

        async def run():
            tasks = []
            for param in params:
                tasks.append(task(param))
            await asyncio.wait(tasks)

        self.loop.run_until_complete(run())
