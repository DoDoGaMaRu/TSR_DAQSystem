from abc import ABC, abstractmethod
from typing import List, Dict
from pandas import DataFrame

from config import ModelConfig
from model.lstm_ae import LstmAE

class ResultHandler(ABC):
    @abstractmethod
    async def __call__(self, score):
        pass


class FaultDetector:
    def __init__(self,
                 model_path: str,
                 channel_names: List[str],
                 result_handler: ResultHandler):

        # TODO 센서별로 초기화 되게끔 변경
        self.model = LstmAE()
        self.model.build((None, ModelConfig.SEQ_LEN, ModelConfig.INPUT_DIM))
        self.model.load_weights(model_path)
        self.result_handler = result_handler
        self.channel_names = sorted(channel_names)
        self._reset_observations()

    def _reset_observations(self):
        self.observations: Dict[str, list] = {name: [] for name in sorted(self.channel_names)}

    async def add_data(self, named_datas: dict):
        for name, data in named_datas.items():
            if len(self.observations[name]) < self.model.batch_size:
                self.observations[name] += data
        await self._trigger()

    async def _trigger(self):
        if self._is_batch():
            self.data_list = list(map(lambda e: e[:self.model.batch_size], self.observations.values()))
            self._reset_observations()

            data = DataFrame()
            for channel_idx in range(len(self.channel_names)):
                data[self.channel_names[channel_idx]] = self.data_list[channel_idx]
            score = await self.model.detect(data)

            await self.result_handler(score)

    def _is_batch(self):
        is_batch = True
        for data in self.observations.values():
            if len(data) < self.model.batch_size:
                is_batch = False
        return is_batch
