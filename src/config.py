import yaml
from dataclasses import dataclass
from typing import List

config_file = 'resources/config.yml'


@dataclass
class DeviceConfig:
    NAME            : str
    TYPE            : str
    CHANNEL         : str
    CHANNEL_NAMES   : List[str]


with open(config_file, 'r', encoding='UTF-8') as yml:
    cfg = yaml.safe_load(yml)


class ClientConfig:
    HOST                : str = cfg['CLIENT']['HOST']
    PORT                : int = cfg['CLIENT']['PORT']
    MACHINE_NAME        : str = cfg['CLIENT']['MACHINE_NAME']
    TIMEOUT             : int = cfg['CLIENT']['TIMEOUT']


class SensorConfig:
    MIN_SAMPLING_RATE   : int = 2400
    RATE                : int = cfg['SENSOR']['RATE'] if int(cfg['SENSOR']['RATE']) > MIN_SAMPLING_RATE else MIN_SAMPLING_RATE
    NUMBER_OF_SAMPLES   : int = cfg['SENSOR']['RATE']
    READ_TIMEOUT        : int = cfg['SENSOR']['READ_TIMEOUT']
    DEVICES             : List[DeviceConfig] = [DeviceConfig(**parm) for parm in cfg['SENSOR']['DEVICES']]


class FileConfig:
    DIRECTORY           : str = cfg['FILE']['DIRECTORY']
    EXTERNAL_DIRECTORY  : str = cfg['FILE']['EXTERNAL_DIRECTORY'] if cfg['FILE']['EXTERNAL_DIRECTORY'] != 'None' else None


class ModelConfig:
    SEQ_LEN             : int = cfg['MODEL']['SEQ_LEN']
    LATENT_DIM          : int = cfg['MODEL']['LATENT_DIM']
    INPUT_DIM           : int = len([channel_name for device_config in SensorConfig.DEVICES for channel_name in device_config.CHANNEL_NAMES])
    TEST_SIZE           : float = cfg['MODEL']['TEST_SIZE']
    LEARNING_RATE       : float = cfg['MODEL']['LEARNING_RATE']