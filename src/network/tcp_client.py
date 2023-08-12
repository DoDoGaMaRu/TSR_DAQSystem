# lib
import asyncio
from asyncio import transports, Protocol

# custom module
from .protocols import tcp_send_protocol

# https://stackoverflow.com/questions/25998394/how-to-reconnect-a-socket-on-asyncio
class TCPClientProtocol(Protocol):
    def __init__(self, client_name):
        self.client_name = client_name
        self.transport = None

    def connection_made(self, transport: transports.WriteTransport) -> None:
        self.transport = transport
        self.transport.write(self.client_name.encode() + b'\n')

    def send_data(self, event, data):
        self.transport.write(tcp_send_protocol(event=event,
                                               data=data))

    def connection_lost(self, exc) -> None:
        self.transport.close()
        self.transport = None
        print('connection lost')


class TCPClient:
    def __init__(self, host, port, name):
        self.host = host
        self.port = port
        self.name = name

        self.transport = None
        self.protocol = None
        self.conn = None

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.create_connection())

    async def create_connection(self):
        loop = asyncio.get_event_loop()
        self.conn = loop.create_connection(lambda: TCPClientProtocol(self.name), self.host, self.port)
        while True:
            try:
                self.transport, self.protocol = loop.run_until_complete(self.conn)
                break
            except:
                print('reconn...')
                await asyncio.sleep(5)

    async def send_data(self, event, data):
        self.protocol.send_data(event, data)

