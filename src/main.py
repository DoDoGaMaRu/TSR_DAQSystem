import asyncio
import time
import random

from network import TCPClient


HOST = 'localhost'
PORT = 8082

machine_name = 'test'

tcp_client = TCPClient(host=HOST,
                       port=PORT,
                       name=machine_name)


async def temp():
    while True:
        await asyncio.sleep(1)
        print('data create')
        if not tcp_client.is_closing():
            tcp_client.send_data(event='vib', data=random.random())


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(temp())
