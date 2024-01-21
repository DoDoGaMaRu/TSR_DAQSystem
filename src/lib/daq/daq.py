import nidaqmx
import asyncio
from typing import List, Dict

from .ni_device import NIDevice
from .data_handler import DataHandler


class DAQ:
    def __init__(self, ni_devices: List[NIDevice]):
        self._ni_devices: List[NIDevice] = ni_devices
        self._data_handlers: List[DataHandler] = []
        self._loop = asyncio.get_event_loop()

    def register_data_handler(self, data_handler: DataHandler) -> None:
        self._data_handlers.append(data_handler)

    def remove_data_handler(self, data_handler: DataHandler) -> None:
        if data_handler in self._data_handlers:
            self._data_handlers.remove(data_handler)

    def read_start(self) -> None:
        for ni_device in self._ni_devices:
            self._loop.create_task(self._read_loop(ni_device))

    async def _read_loop(self, device: NIDevice) -> None:
        while True:
            try:
                named_datas = await device.read()
                self._loop.create_task(self._data_notify(device.name(), named_datas))
                await asyncio.sleep(1)
            except nidaqmx.errors.DaqReadError:
                pass
            except Exception as err:
                print(f'Undefined Error : \n{str(err)}')

    async def _data_notify(self, device_name: str, named_datas: Dict[str, List[float]]) -> None:
        for handler in self._data_handlers:
            try:
                self._loop.create_task(handler.data_update(device_name, named_datas))
            except Exception as err:
                print(f'Data Handling Error : \n{str(err)}')
