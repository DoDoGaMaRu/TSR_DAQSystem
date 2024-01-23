import asyncio
from typing import Dict
from scipy import signal

from config import NIDeviceType
from .machine_client import MachineClient
from .machine import EventHandler
from .machine.machine_event import MachineEvent

MAXIMUM_RATE: int = 30


class DataSender(EventHandler):
    def __init__(self,
                 name: str,
                 host: str,
                 port: int,
                 timeout: int,
                 sensor_types: Dict[str, NIDeviceType]):
        self.name = name
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sensor_types = sensor_types

        self.transport = None
        self.protocol = None
        self.conn = None

        self._loop = asyncio.get_event_loop()
        self._loop.create_task(self.permanent_connection())

    async def permanent_connection(self) -> None:
        while True:
            try:
                self.conn = self._loop.create_connection(protocol_factory=lambda: MachineClient(self.name),
                                                         host=self.host,
                                                         port=self.port)
                self.transport, self.protocol = await self.conn
                await self.protocol.wait()
            except Exception:
                await asyncio.sleep(self.timeout)

    async def event_handle(self, event: MachineEvent, data: Dict) -> None:
        if not self.is_closing():
            event, data = self.convert(event, data)
            self.protocol.send_data(event=event, data=data)

    def is_closing(self) -> bool:
        return self.protocol is None or self.protocol.is_closing()

    def convert(self, event: MachineEvent, data: Dict):
        if event is MachineEvent.DataUpdate:
            data = {
                sensor: {
                    'type': self.sensor_types[sensor].name,
                    'data': signal.resample(s_data, MAXIMUM_RATE).tolist() if MAXIMUM_RATE < len(s_data) else s_data
                } for sensor, s_data in data.items()
            }
        elif event is MachineEvent.FaultDetect:
            """
            data = {
                'score': int,
                'threshold': int
            }
            """
            pass
        else:
            raise RuntimeError('Undefined Event')

        return event.name, data
