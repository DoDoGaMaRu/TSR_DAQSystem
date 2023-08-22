import asyncio

from asyncio import Protocol, Event, transports

from .protocols import tcp_send_protocol


class MachineProtocol(Protocol):
    def __init__(self, name):
        self.name = name

        self.event = Event()
        self.transport = None
        self.writer = None
        self.reader = None

    def connection_made(self, transport: transports.WriteTransport) -> None:
        self.transport = transport
        self.reader = asyncio.StreamReader(loop=asyncio.get_event_loop())
        self.writer = asyncio.StreamWriter(transport=transport,
                                           protocol=self,
                                           reader=self.reader,
                                           loop=asyncio.get_event_loop())
        self.send_data(event='name', data=self.name)
        print(f'{self.name} connection made')

    def send_data(self, event, data) -> None:
        tcp_send_protocol(writer=self.writer,
                          event=event,
                          data=data)

    def is_closing(self) -> bool:
        return self.writer.is_closing()

    def connection_lost(self, exc) -> None:
        self.writer.close()
        print(f'{self.name} connection lost')
        self.event.set()

    async def wait(self):
        await self.event.wait()


class DataSender:
    def __init__(self,
                 name: str,
                 host: str,
                 port: int,
                 timeout: int = 30):
        self.name = name
        self.host = host
        self.port = port
        self.timeout = timeout

        self.transport = None
        self.protocol = None
        self.conn = None

    async def permanent_connection(self):
        loop = asyncio.get_event_loop()

        while True:
            try:
                self.conn = loop.create_connection(protocol_factory=lambda: MachineProtocol(self.name),
                                                   host=self.host,
                                                   port=self.port)
                self.transport, self.protocol = await self.conn
                await self.protocol.wait()
            except Exception:
                await asyncio.sleep(self.timeout)

    def send_data(self, event, data):
        self.protocol.send_data(event=event, data=data)

    def is_closing(self) -> bool:
        return self.protocol is None or self.protocol.is_closing()
