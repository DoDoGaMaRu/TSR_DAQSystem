# lib
import asyncio
from asyncio import Protocol, Event, transports

# custom module
from .protocols import tcp_send_protocol

TIMEOUT = 10


class TCPClientProtocol(Protocol):
    def __init__(self, client_name):
        self.client_name = client_name
        self.transport = None
        self.event = Event()

    def connection_made(self, transport: transports.WriteTransport) -> None:
        self.transport = transport
        self.transport.write(self.client_name.encode() + b'\n')
        print('connection_made')

    def send_data(self, event, data) -> None:
        if not self.transport.is_closing():
            self.transport.write(tcp_send_protocol(event=event, data=data))
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


class TCPClient:
    def __init__(self, host, port, name):
        self.host = host
        self.port = port
        self.name = name

        self.transport = None
        self.protocol = None
        self.conn = None

        loop = asyncio.get_event_loop()
        loop.create_task(self.create_connection())

    async def create_connection(self):
        loop = asyncio.get_event_loop()

        while True:
            try:
                self.conn = loop.create_connection(lambda: TCPClientProtocol(self.name), self.host, self.port)
                self.transport, self.protocol = await self.conn
                await self.protocol.wait()
            except ConnectionRefusedError:
                print('disconnected')
                await asyncio.sleep(TIMEOUT)

    def send_data(self, event, data) -> None:
        self.protocol.send_data(event=event, data=data)
        print('data send')

    def is_closing(self):
        return self.protocol is None or self.protocol.is_closing()
