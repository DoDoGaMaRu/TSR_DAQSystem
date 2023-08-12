import asyncio

from network import TCPClient


HOST = 'localhost'
PORT = 8082

machine_name = 'test'

tcp_client = TCPClient(host=HOST,
                       port=PORT,
                       name=machine_name)
loop = asyncio.get_event_loop()


async def temp():
    while True:
        await tcp_client.send_data(event='',
                             data=input('send : '))
        await asyncio.sleep(0.1)

loop.run_until_complete(temp())
