import asyncio

from abc import ABC, abstractmethod

import nidaqmx
from typing import Union, List, Dict

from .ni_device import NIDevice, DeviceConfig


class DataHandler(ABC):
    @abstractmethod
    async def __call__(self, device_name: str, named_datas: Dict):
        pass


class DAQ:
    def __init__(self,
                 rate: int,
                 device_config: Union[DeviceConfig, List[DeviceConfig]],
                 data_handler: DataHandler):
        self.rate = rate
        self.device_config = device_config if isinstance(device_config, List) else [device_config]
        self.data_handler = data_handler

        self.devices = {f'{conf.TYPE.name}.{conf.NAME}': NIDevice(conf=conf) for conf in self.device_config}

    def read_forever(self):
        loop = asyncio.get_event_loop()
        for name, device in self.devices.items():
            loop.create_task(self._read_loop(name, device))

    async def _read_loop(self, name, device: NIDevice):
        loop = asyncio.get_event_loop()
        while True:
            try:
                named_datas = await device.read()
                loop.create_task(self.data_handler(device_name=name, named_datas=named_datas))
                await asyncio.sleep(1)
            except nidaqmx.errors.DaqReadError:
                pass
            except Exception as err:
                print(f'정의되지 않은 오류\n{str(err)}')
