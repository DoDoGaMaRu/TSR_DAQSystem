import yaml
from typing import List

from daq_system.machine import MachineConfig
from daq_system.daq.ni_device import DeviceConfig

config_file = '../src/resources/config.yml'
with open(config_file, 'r', encoding='UTF-8') as yml:
    cfg = yaml.safe_load(yml)


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
    INPUT_DIM           : int = len([channel_name for device_config in DAQConfig.DEVICES for channel_name in device_config.CHANNEL_NAMES])
    TEST_SIZE           : float = cfg['MODEL']['TEST_SIZE']
    LEARNING_RATE       : float = cfg['MODEL']['LEARNING_RATE']
    EPOCH               : int = cfg['MODEL']['EPOCH']
    BATCH_SIZE          : int = cfg['MODEL']['BATCH_SIZE']