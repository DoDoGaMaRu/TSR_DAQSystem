from .csvController import CsvController
from config import FileConfig
from typing import Dict


class RawdataController:
    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.cc_list: Dict[str, CsvController] = {}

    async def add_data(self, device_name: str, message: dict):
        if device_name not in self.cc_list:
            self.cc_list[device_name] = CsvController(device_name=device_name,
                                                      header=list(message.keys()),
                                                      directory=FileConfig.DIRECTORY,
                                                      external_directory=FileConfig.EXTERNAL_DIRECTORY)
        cols = list(message.values())
        cols[0] = [message['time'] for _ in range(len(cols[1]))]
        await self.cc_list[device_name].add_data(cols)
