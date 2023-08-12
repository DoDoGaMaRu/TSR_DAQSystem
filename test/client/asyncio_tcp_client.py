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


def send_protocol(event, data):
    with io.BytesIO() as memfile:
        pickle.dump((event, data), memfile)
        serialized = memfile.getvalue()
    return serialized + b'\n'


async def save_loop(msg: float) -> None:
    # TODO 데이터 저장 로직 구현
    print('data save')
    await asyncio.sleep(1)


async def send_loop(protocol: TCPClientProtocol, msg: float) -> None:
    protocol.send_data(event='test', data=msg)
    print('data send')
    await asyncio.sleep(1)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    protocol: TCPClientProtocol = None

    while True:
        msg = random.random()

        if protocol is not None and not protocol.is_closing():
            loop.run_until_complete(send_loop(protocol, msg))
        else:
            try:
                conn = loop.create_connection(lambda: TCPClientProtocol(), HOST, PORT)
                result = loop.run_until_complete(asyncio.gather(save_loop(msg), conn))
                transport, protocol = result[1]
            except ConnectionRefusedError:
                pass
