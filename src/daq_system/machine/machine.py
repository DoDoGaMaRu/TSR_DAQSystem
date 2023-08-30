import asyncio

from typing import Dict

from config import MachineConfig
from util.clock import get_time
from .csv_controller import CsvController
from .data_sender import DataSender
from .fault_detector import FaultDetector, ResultHandler


class AnomalyHandler(ResultHandler):
    def __init__(self, data_sender: DataSender, threshold: int):
        self.data_sender = data_sender
        self.threshold = threshold

    async def __call__(self, score):
        anomaly = score > self.threshold

        if not self.data_sender.is_closing():
            self.data_sender.send_data(event='anomaly', data={
                'score': score,
                'threshold': self.threshold,
                'anomaly': anomaly
            })
        # TODO 결과는 이곳에서 후킹, GUI 개발 시에도 동일하게 이용


class Machine:
    def __init__(self,
                 conf: MachineConfig,
                 save_path: str,
                 send_path: str = None):
        self.name = conf.NAME
        self.channel_names = conf.CHANNEL_NAMES

        self.data_send_mode = conf.DATA_SEND_MODE
        self.fault_detect_mode = conf.FAULT_DETECT_MODE

        # DATA SEND MODE
        if self.data_send_mode:
            self.data_sender = DataSender(name=self.name,
                                          host=conf.HOST,
                                          port=conf.PORT,
                                          timeout=conf.TIMEOUT)
            loop = asyncio.get_event_loop()
            loop.create_task(self.data_sender.permanent_connection())

        # FAULT DETECT MODE
        if self.fault_detect_mode:
            anomaly_handler = AnomalyHandler(data_sender=self.data_sender,
                                             threshold=conf.THRESHOLD)
            self.fault_detector = FaultDetector(model_path=conf.FAULT_DETECT_MODEL,
                                                channel_names=self.channel_names,
                                                result_handler=anomaly_handler)

        # DATA SAVE
        self.directory = f'{save_path}\\{self.name}'
        self.external_directory = f'{send_path}\\{self.name}' if send_path is not None else None
        self.file_writers: Dict[str, CsvController] = {}

    def _add_csv_controller(self, channel_name: str):
        self.file_writers[channel_name] = CsvController(name=channel_name,
                                                        header=['time', channel_name],
                                                        directory=self.directory,
                                                        external_directory=self.external_directory)

    async def _data_processing(self, device_name: str, named_datas: dict):
        cur_time = get_time()

        if self.data_send_mode and not self.data_sender.is_closing():
            self.data_sender.send_data(event=device_name, data=named_datas)

        if self.fault_detect_mode:
            await self.fault_detector.add_data(named_datas)

        for channel_name, data in named_datas.items():
            if channel_name not in self.file_writers:
                self._add_csv_controller(channel_name)
            cols = [[cur_time for _ in data], data]
            await self.file_writers[channel_name].add_data(cols)

    async def data_hooking(self, device_name: str, named_datas: dict):
        named_datas = {name: data for name, data in named_datas.items() if name in self.channel_names}
        if len(named_datas) > 0:
            await self._data_processing(device_name, named_datas)
