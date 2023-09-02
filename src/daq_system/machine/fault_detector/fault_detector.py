import tarfile
import tempfile

from abc import ABC, abstractmethod
from typing import List, Dict

import yaml
from pandas import DataFrame
from dataclasses import dataclass

from model.lstm_ae import LstmAE
from config import MODEL_PATH


@dataclass
class ModelConfig:
    NAME            : str
    BATCH_SIZE      : int
    LATENT_DIM      : int
    SEQ_LEN         : int
    THRESHOLD       : int


class ResultHandler(ABC):
    @abstractmethod
    async def __call__(self, score):
        pass


class FaultDetector:
    def __init__(self,
                 machine_name: str,
                 channel_names: List[str],
                 result_handler: ResultHandler):
        self.machine_name = machine_name
        self.result_handler = result_handler
        self.channel_names = channel_names
        self._reset_observations()
        self.models: Dict[str, LstmAE] = {}
        self._init_models()

    def _init_models(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with tarfile.open(f'{MODEL_PATH}/{self.machine_name}.tar', 'r') as tar_file:
                tar_file.extractall(path=f'{tmpdir}\\{self.machine_name}')

            with open(f'{tmpdir}\\{self.machine_name}\\METADATA.yml', 'r', encoding='UTF-8') as yml:
                cfg = yaml.safe_load(yml)

            for conf in [ModelConfig(**parm) for parm in cfg['MODELS']]:
                model = LstmAE(seq_len=conf.SEQ_LEN,
                               input_dim=1,
                               latent_dim=conf.LATENT_DIM,
                               batch_size=conf.BATCH_SIZE,
                               threshold=conf.THRESHOLD)
                model.load(f'{tmpdir}\\{self.machine_name}\\{conf.NAME}.h5')
                self.models[conf.NAME] = model

    def _reset_observations(self):
        self.observations: Dict[str, list] = {name: [] for name in sorted(self.channel_names)}

    async def add_data(self, named_datas: dict):
        for name, data in named_datas.items():
            if len(self.observations[name]) < 300:
                self.observations[name] += data
        await self._trigger()

    async def _trigger(self):
        if self._is_batch():
            await self._fault_detect()
            self._reset_observations()

    async def _fault_detect(self):
        target_data = {name: data[:self.models[name].batch_size]
                       for name, data in self.observations.items()}

        score = 0
        for name in self.channel_names:
            data = DataFrame()
            data['data'] = target_data[name]
            score += await self.models[name].detect(data)

        await self.result_handler(score)

    def _is_batch(self):
        is_batch = True
        for name, data in self.observations.items():
            if len(data) < self.models[name].batch_size:
                is_batch = False
        return is_batch
