import asyncio
import logging
import unittest

import yaml

import netdev

logging.basicConfig(filename="unittest.log", level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class TestCisco(unittest.TestCase):
    def load_credits(self):
        creds = "cisco_ios_credits.yaml"
        params = yaml.load(open(creds, 'r'))
        return params

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        self.loop.set_debug(False)
        asyncio.set_event_loop(self.loop)

    def test_show_hostname(self):
        params = self.load_credits()

        async def task(param):
            br = netdev.connect(**param)
            await br.connect()
            out = await br.send_command('show run | i hostname')
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
            br = netdev.connect(**param)
            await br.connect()
            commands = ["dir", "show ver", "show run", "show ssh"]
            for cmd in commands:
                out = await br.send_command(cmd)

        async def run():
            tasks = []
            for param in params:
                tasks.append(task(param))
            await asyncio.wait(tasks)

        self.loop.run_until_complete(run())

    def test_config_set(self):
        params = self.load_credits()

        async def task(param):
            br = netdev.connect(**param)
            await br.connect()
            commands = ["int fa0/0", "exit"]
            out = await br.send_config_set(commands)
            self.assertIn("int fa0/0", out)
            self.assertIn("exit", out)

        async def run():
            tasks = []
            for param in params:
                tasks.append(task(param))
            await asyncio.wait(tasks)

        self.loop.run_until_complete(run())
