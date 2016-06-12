import asyncio

import yaml

import netdev

creds = 'device_credits.yaml'


# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


async def task(param):
    ios = netdev.connect(**param)
    await ios.connect()
    out = await ios.send_command("show ssh")
    print(out)


async def run():
    devices = yaml.load(open(creds, 'r'))
    params = [p for p in devices if p['device_type'] == 'cisco_ios']
    tasks = []
    params = [params[0]]
    for param in params:
        tasks.append(task(param))
    await asyncio.wait(tasks)


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
