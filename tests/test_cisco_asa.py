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
                asa = netdev.connect(**dev)
                await asa.connect()
                out = await asa.send_command('show run | i hostname')
                self.assertIn("hostname", out)
                await asa.disconnect()

        self.loop.run_until_complete(task())

    def test_show_several_commands(self):
        async def task():
            for dev in self.devices:
                asa = netdev.connect(**dev)
                await asa.connect()
                commands = ["show ver", "show run", "show ssh"]
                for cmd in commands:
                    out = await asa.send_command(cmd, strip_command=False)
                    self.assertIn(cmd, out)
                await asa.disconnect()

        self.loop.run_until_complete(task())

    def test_config_set(self):
        async def task():
            for dev in self.devices:
                asa = netdev.connect(**dev)
                await asa.connect()
                commands = ["interface Management0/0", "exit"]
                out = await asa.send_config_set(commands)
                self.assertIn("interface Management0/0", out)
                self.assertIn("exit", out)
                await asa.disconnect()

        self.loop.run_until_complete(task())

    def test_current_context(self):
        async def task():
            for dev in self.devices:
                asa = netdev.connect(**dev)
                await asa.connect()
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

                await asa.disconnect()

        self.loop.run_until_complete(task())
