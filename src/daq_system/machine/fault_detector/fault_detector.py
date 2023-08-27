from typing import List, Dict
from abc import ABC, abstractmethod
from models.lstm_ae import LstmAE
from config import ModelConfig
from pandas import DataFrame


class ResultHandler(ABC):
    @abstractmethod
    async def __call__(self, score):
        pass


class FaultDetector:
    def __init__(self,
                 model_path: str,
                 channel_names: List[str],
                 result_handler: ResultHandler):

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
            # 해당 배치 내에서 비정상이라고 판단된 시점의 수
            anomalies = self.model.detect(DataFrame(self.data_list))
            await self.result_handler(anomalies)

    def _is_batch(self):
        is_batch = True
        for data in self.observations.values():
            if len(data) < self.model.batch_size:
                is_batch = False
        return is_batch
