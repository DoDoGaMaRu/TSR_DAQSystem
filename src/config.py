import yaml
from typing import List
from dataclasses import dataclass

from daq_system.daq.ni_device import DeviceConfig

config_file = '../src/resources/config.yml'
with open(config_file, 'r', encoding='UTF-8') as yml:
    cfg = yaml.safe_load(yml)


@dataclass
class MachineConfig:
    NAME                : str
    CHANNEL_NAMES       : List[str]

    DATA_SEND_MODE      : bool
    FAULT_DETECT_MODE   : bool

    HOST                : str = None
    PORT                : int = None
    TIMEOUT             : int = 60

    FAULT_DETECT_MODEL  : str = None
    THRESHOLD           : int = None

    def __post_init__(self):
        if self.DATA_SEND_MODE:
            if self.HOST is None:
                raise ValueError(f'{self.NAME} : missing host')
            if self.PORT is None:
                raise ValueError(f'{self.NAME} : missing port')

        if self.FAULT_DETECT_MODE:
            if self.FAULT_DETECT_MODEL is None:
                raise ValueError(f'{self.NAME} : missing model path')
            if self.THRESHOLD is None:
                raise ValueError(f'{self.NAME} : missing threshold')


class DAQConfig:
    RATE                : int = cfg['DAQ']['RATE']
    DEVICES             : List[DeviceConfig] = [DeviceConfig(**parm, RATE=cfg['DAQ']['RATE']) for parm in cfg['DAQ']['DEVICES']]


class MachineClientConfig:
    MACHINES            : List[MachineConfig] = [MachineConfig(**parm) for parm in cfg['MACHINE']]


class FileConfig:
    SAVE_PATH           : str = cfg['FILE']['SAVE_PATH']
    SEND_PATH           : str = cfg['FILE']['SEND_PATH'] if cfg['FILE']['SEND_PATH'] != '' else None


class ModelConfig:
    SEQ_LEN             : int = cfg['MODEL']['SEQ_LEN']
    LATENT_DIM          : int = cfg['MODEL']['LATENT_DIM']
    INPUT_DIM           : int = len(DAQConfig.DEVICES)
    LEARNING_RATE       : float = cfg['MODEL']['LEARNING_RATE']
    EPOCH               : int = cfg['MODEL']['EPOCH']
    BATCH_SIZE          : int = cfg['MODEL']['BATCH_SIZE'] - SEQ_LEN
    THRESHOLD           : float = cfg['MODEL']['THRESHOLD']
