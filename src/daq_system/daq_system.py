from typing import Dict, List

from .machine import Machine
from .daq import DAQ, DataHandler
from config import DAQConfig, MachineClientConfig, FileConfig


class DataDivider(DataHandler):
    def __init__(self, machines: List[Machine]):
        self.machines = machines

    async def __call__(self, device_name: str, named_datas: Dict):
        for machine in self.machines:
            await machine.data_hooking(device_name, named_datas)
        # TODO GUI 개발 시, 데이터는 이곳에서 후킹


class DAQSystem:
    def __init__(self):
        self.machines = [Machine(conf=conf,
                                 save_path=FileConfig.SAVE_PATH,
                                 send_path=FileConfig.SEND_PATH)
                         for conf in MachineClientConfig.MACHINES]

        self.daq = DAQ(rate=DAQConfig.RATE,
                       device_config=DAQConfig.DEVICES,
                       data_handler=DataDivider(machines=self.machines))

    def run(self):
        self.daq.read_forever()
