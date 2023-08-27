import io
import pickle
import asyncio
import random
from asyncio import transports

HOST = 'localhost'
PORT = 8082

machine_name = 'test'


class TCPClientProtocol(asyncio.Protocol):
    def __init__(self):
        self.transport = None
        self.event = asyncio.Event()

    def connection_made(self, transport: transports.WriteTransport) -> None:
        self.transport = transport
        self.transport.write(machine_name.encode() + b'\n')
        print('connection made')

    def send_data_with_extrainfo(self, data, extrainfo) -> None:
        message = f"{data}:{extrainfo}\n".encode()
        self.transport.write(message)

    def send_data(self, event, data) -> None:
        if not self.transport.is_closing():
            self.transport.write(send_protocol(event=event,
                                               data=data))
        else:
            raise Exception("Attempted to send data but lost connection")

    def is_closing(self) -> bool:
        return self.transport.is_closing()

    def connection_lost(self, exc) -> None:
        self.transport.close()
        print('connection lost')
        self.event.set()

    async def wait(self):
        await self.event.wait()


protocol: TCPClientProtocol = None


def send_protocol(event, data):
    with io.BytesIO() as memfile:
        pickle.dump((event, data), memfile)
        serialized = memfile.getvalue()
    return serialized + b'\n'


async def save_loop(msg: float) -> None:
    print('data save')
    await asyncio.sleep(1)


async def send_loop() -> None:
    global protocol
    while True:
        msg = random.random() # get_vib()
        print('save')
        if protocol is not None and not protocol.is_closing():
            protocol.send_data(event='test', data=msg)
            print('data send')
        await asyncio.sleep(1)


async def create_conn():
    global protocol
    while True:
        try:
            conn = loop.create_connection(lambda: TCPClientProtocol(), HOST, PORT)
            transport, protocol = await conn
            await protocol.wait()
        except ConnectionRefusedError:
            print('disconnected')
            await asyncio.sleep(10)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(send_loop())
    loop.run_until_complete(create_conn())
