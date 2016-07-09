import asyncio
import logging
import unittest

import yaml

import netdev

logging.basicConfig(filename="unittest.log", level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def load_credits():
    config_path = 'config.yaml'
    config = yaml.load(open(config_path, 'r'))
    devices = yaml.load(open(config['device_credentials'], 'r'))
    params = [p for p in devices if p['device_type'] == 'mikrotik_routeros']
    return params


class TestCisco(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        self.loop.set_debug(False)
        asyncio.set_event_loop(self.loop)

    def test_show_system_identity(self):
        params = load_credits()

        async def task(param):
            mik = netdev.connect(**param)
            await mik.connect()
            out = await mik.send_command('/system identity print')
            self.assertIn(mik.base_prompt, out)
            await mik.disconnect()

        async def run():
            tasks = []
            for param in params:
                tasks.append(task(param))
            await asyncio.wait(tasks)

        self.loop.run_until_complete(run())

    def test_show_several_commands(self):
        params = load_credits()

        async def task(param):
            mik = netdev.connect(**param)
            await mik.connect()
            commands = ["/ip address print", "/system package print", " /user print"]
            for cmd in commands:
                out = await mik.send_command(cmd, strip_command=False)
                self.assertIn(cmd, out)
            await mik.disconnect()

        async def run():
            tasks = []
            for param in params:
                tasks.append(task(param))
            await asyncio.wait(tasks)

        self.loop.run_until_complete(run())
