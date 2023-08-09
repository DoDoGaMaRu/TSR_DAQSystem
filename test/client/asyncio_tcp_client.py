import io
import pickle
import asyncio
from asyncio import transports

HOST = '192.168.0.8'
PORT = 8082

machine_name = 'test'

# TODO 연결 상태 확인 및 재연결 알고리즘 추가
class TCPClientProtocol(asyncio.Protocol):
    def connection_made(self, transport: transports.WriteTransport) -> None:
        self.transport = transport
        self.transport.write(machine_name.encode() + b'\n')

    def send_data_with_extrainfo(self, data, extrainfo):
        message = f"{data}:{extrainfo}\n".encode()
        self.transport.write(message)

    def send_data(self, event, data):
        self.transport.write(send_protocol(event=event,
                                           data=data))

    def connection_lost(self, exc) -> None:
        self.transport.close()
        print('connection lost')


def send_protocol(event, data):
    with io.BytesIO() as memfile:
        pickle.dump((event, data), memfile)
        serialized = memfile.getvalue()
    return serialized + b'\n'


async def msg_loop(protocol):
    while True:
        msg = input('send : ')
        protocol.send_data(event='test', data=msg)
        await asyncio.sleep(0.1)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    while True:
        try:
            conn = loop.create_connection(lambda: TCPClientProtocol(), HOST, PORT)
            protocol: TCPClientProtocol
            transport, protocol = loop.run_until_complete(conn)
            loop.run_until_complete(msg_loop(protocol))
        except Exception:
            pass
