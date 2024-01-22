import asyncio
from typing import Dict

from lib.tcp_client.tcp_client import TCPClient
from .machine import EventHandler
from .machine.event import Event


class DataSender(EventHandler):
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

    async def permanent_connection(self) -> None:
        loop = asyncio.get_event_loop()

        while True:
            try:
                self.conn = loop.create_connection(protocol_factory=lambda: TCPClient(self.name),
                                                   host=self.host,
                                                   port=self.port)
                self.transport, self.protocol = await self.conn
                await self.protocol.wait()
            except Exception:
                await asyncio.sleep(self.timeout)

    async def event_handle(self, event: Event, data: Dict) -> None:
        # TODO rate가 높은 경우, 특정 크기 이하로 조정
        if not self.is_closing():
            self.protocol.send_data(event=event, data=data)

    def is_closing(self) -> bool:
        return self.protocol is None or self.protocol.is_closing()
