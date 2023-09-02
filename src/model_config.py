import yaml

from typing import List
from dataclasses import dataclass


config_file = 'resources/model_config.yml'
with open(config_file, 'r', encoding='UTF-8') as yml:
    cfg = yaml.safe_load(yml)


@dataclass
class TrainConfig:
    SENSOR_NAME     : str
    SEQ_LEN         : int
    LATENT_DIM      : int
    LEARNING_RATE   : float
    EPOCH           : int
    BATCH_SIZE      : int
    THRESHOLD       : int
    INPUT_DIM       : int = 1

    def __post_init__(self):
        # 정보 검증
        pass


class Config:
    DATA_PATH       : str = cfg['DATA_PATH']
    TEST_PATH       : str = cfg['TEST_PATH']
    MODEL_OUT       : str = cfg['MODEL_OUT']
    NAME            : str = cfg['MACHINE']['NAME']
    TRAIN           : List[TrainConfig] = [TrainConfig(**parm) for parm in cfg['TRAIN']]
