import asyncio
import logging

import yaml

import netdev

creds = "cisco_ios_credits.yaml"

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


async def task(param):
    br = netdev.connect(**param)
    await br.connect()
    out = await br.send_command("sh ver")
    prompt = await br.find_prompt()
    print("{0} Done".format(prompt, out))


async def run():
    params = yaml.load(open(creds, 'r'))
    tasks = []
    for param in params:
        tasks.append(task(param))
    await asyncio.wait(tasks)


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
