# lib
import asyncio
from asyncio import Protocol, Event, transports

# custom module
from .protocols import tcp_send_protocol


class TCPClientProtocol(Protocol):
    def __init__(self, client_name):
        self.client_name = client_name
        self.transport = None
        self.event = Event()

    def connection_made(self, transport: transports.WriteTransport) -> None:
        transport.write(self.client_name.encode() + b'\o')
        self.transport = transport
        print('connection made')

    def send_data(self, event, data) -> None:
        self.transport.write(tcp_send_protocol(event=event, data=data))

    def is_closing(self) -> bool:
        return self.transport.is_closing()

    def connection_lost(self, exc) -> None:
        self.transport.close()
        print('connection lost')
        self.event.set()

    async def wait(self):
        await self.event.wait()


class TCPClient:
    def __init__(self,
                 host: str,
                 port: int,
                 name: str,
                 timeout: int = 30):
        self.host = host
        self.port = port
        self.name = name
        self.timeout = timeout

        self.transport = None
        self.protocol = None
        self.conn = None

    async def permanent_connection(self):
        loop = asyncio.get_event_loop()

        while True:
            try:
                self.conn = loop.create_connection(lambda: TCPClientProtocol(self.name), self.host, self.port)
                self.transport, self.protocol = await self.conn
                await self.protocol.wait()
            except ConnectionRefusedError:
                await asyncio.sleep(self.timeout)

    def send_data(self, event, data) -> None:
        self.protocol.send_data(event=event, data=data)

    def is_closing(self):
        return self.protocol is None or self.protocol.is_closing()
