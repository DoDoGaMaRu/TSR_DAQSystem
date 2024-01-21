import asyncio

import yaml
from typing import Dict, List
from pandas import DataFrame

from lib.daq import DataHandler
from lib.lstm_ae import LstmAE, ModelConfig
from config.paths import MODEL_DIR
from .event import Event
from .event_handler import EventHandler


class Machine(DataHandler):
    def __init__(self,
                 name: str,
                 sensors: List[str],
                 fault_detectable: bool = False,
                 fault_threshold: int = 0):
        self._name: str = name
        self._sensors: List[str] = sensors
        self._fault_detectable: bool = fault_detectable
        self._fault_threshold: int = fault_threshold

        self._loop = asyncio.get_event_loop()
        self._event_handlers: List[EventHandler] = []

        if self._fault_detectable:
            self._models: Dict[str, LstmAE] = {}
            self._batches: Dict[str, List] = {}
            self._init_models()
            self._init_batches()

    def get_name(self) -> str:
        return self._name

    def get_sensors(self) -> List[str]:
        return self._sensors

    def is_fault_detectable(self):
        return self._fault_detectable

    def _init_models(self) -> None:
        try:
            with open(f'{MODEL_DIR}\\{self._name}\\METADATA.yml', 'r', encoding='UTF-8') as yml:
                cfg = yaml.safe_load(yml)

            for conf in [ModelConfig(**parm) for parm in cfg['MODELS']]:
                model = LstmAE(seq_len=conf.SEQ_LEN,
                               input_dim=1,
                               latent_dim=conf.LATENT_DIM,
                               batch_size=conf.BATCH_SIZE,
                               threshold=conf.THRESHOLD)
                model.load(f'{MODEL_DIR}\\{self._name}\\{conf.NAME}.h5')
                self._models[conf.NAME] = model
        except Exception as err:
            self._fault_detectable = False
            print(err)

    def _init_batches(self) -> None:
        self._batches = {name: [] for name in sorted(self._sensors)}

    def register_handler(self, event_handler: EventHandler) -> None:
        self._event_handlers.append(event_handler)

    def remove_handler(self, event_handler: EventHandler) -> None:
        if event_handler in self._event_handlers:
            self._event_handlers.remove(event_handler)

    async def data_update(self, device_name: str, named_datas: Dict[str, List[float]]) -> None:
        named_datas = {sensor: data for sensor, data in named_datas.items() if sensor in self._sensors}

        await self._event_notify(Event.DataUpdate, named_datas)
        if self._fault_detectable:
            await self._fault_detect(named_datas)

    async def _fault_detect(self, named_datas: Dict[str, List[float]]) -> None:
        is_batch = True
        for name, data in named_datas.items():
            if len(self._batches[name]) < self._models[name].batch_size:
                self._batches[name] += data
                is_batch = False

        if is_batch:
            score = 0
            for name in self._sensors:
                target = DataFrame()
                target['data'] = self._batches[name][:self._models[name].batch_size]
                score += await self._models[name].detect(target)
            self._init_batches()

            await self._event_notify(Event.FaultDetect, {
                'score': score,
                'threshold': self._fault_threshold
            })

    async def _event_notify(self, event: Event, data: any) -> None:
        for handler in self._event_handlers:
            try:
                self._loop.create_task(handler.event_handle(event, data))
            except WindowsError as err:
                print(f'Event Handling Error : \n{str(err)}')
            except Exception as err:
                print(f'Event Handling Error : \n{str(err)}')
