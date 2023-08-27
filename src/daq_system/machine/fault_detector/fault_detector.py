from typing import List, Dict
from abc import ABC, abstractmethod


class ResultHandler(ABC):
    @abstractmethod
    async def __call__(self, score):
        pass


class FaultDetector:
    def __init__(self,
                 model_path: str,
                 channel_names: List[str],
                 result_handler: ResultHandler):
        # TODO 모델 로드
        self.result_handler = result_handler
        self.batch_size = 512
        self.channel_names = sorted(channel_names)
        self._reset_observations()

    def _reset_observations(self):
        self.observations: Dict[str, list] = {name: [] for name in sorted(self.channel_names)}

    async def add_data(self, named_datas: dict):
        for name, data in named_datas.items():
            if len(self.observations[name]) < self.batch_size:
                self.observations[name] += data
        await self._trigger()

    async def _trigger(self):
        if self._is_batch():
            self.data_list = list(map(lambda e: e[:self.batch_size], self.observations.values()))
            self._reset_observations()
            # TODO 고장진단
            score = 400
            await self.result_handler(score)

    def _is_batch(self):
        is_batch = True
        for data in self.observations.values():
            if len(data) < self.batch_size:
                is_batch = False
        return is_batch
