import io
import pickle
import asyncio
from asyncio import Protocol, Event, transports

from .tcp_exceptions import SerializeException

SEP         : bytes = b'\o'
SEP_LEN     : int = len(SEP)


class TCPClient(Protocol):
    def __init__(self, name):
        self.name = name

        self._event = Event()
        self._transport = None
        self._writer = None
        self._reader = None

    def connection_made(self, transport: transports.WriteTransport) -> None:
        self._transport = transport
        self._reader = asyncio.StreamReader(loop=asyncio.get_event_loop())
        self._writer = asyncio.StreamWriter(transport=transport,
                                            protocol=self,
                                            reader=self._reader,
                                            loop=asyncio.get_event_loop())
        self.send_data(event='name', data=self.name)
        print(f'{self.name} connection made')

    def send_data(self, event, data) -> None:
        tcp_send_protocol(writer=self._writer,
                          event=event,
                          data=data)

    def is_closing(self) -> bool:
        return self._writer.is_closing()

    def connection_lost(self, exc) -> None:
        self._writer.close()
        print(f'{self.name} connection lost')
        self._event.set()

    async def wait(self):
        await self._event.wait()


def tcp_send_protocol(writer: asyncio.StreamWriter, event, data):
    try:
        with io.BytesIO() as memfile:
            pickle.dump((event, data), memfile)
            serialized = memfile.getvalue()
        writer.write(serialized + SEP)
    except Exception:
        raise SerializeException()
