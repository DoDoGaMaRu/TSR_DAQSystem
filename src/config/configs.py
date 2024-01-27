from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, List
from dataclasses import dataclass


class NIDeviceType(Enum):
    VIB: int = auto()
    TEMP: int = auto()


@dataclass
class SensorConfig:
    NAME        : str
    CHANNEL     : str
    OPTIONS     : Dict[str, any]


@dataclass
class NIDeviceConfig:
    NAME        : str
    TYPE        : NIDeviceType
    RATE        : int
    SENSORS     : List[SensorConfig]

    def __post_init__(self):
        if isinstance(self.SENSORS, Dict):
            self.SENSORS = [SensorConfig(**sensor_conf) for sensor_conf in self.SENSORS]
        if isinstance(self.TYPE, str):
            self.TYPE = NIDeviceType.__members__[self.TYPE]


@dataclass
class ActivableModeConfig(ABC):
    ACTIVATION    : bool

    def __post_init__(self):
        if self.ACTIVATION:
            self.valid_check()

    @abstractmethod
    def valid_check(self) -> None:
        pass


@dataclass
class DataSendModeConfig(ActivableModeConfig):
    HOST            : str = ''
    PORT            : int = 0
    TIMEOUT         : int = 60

    def valid_check(self) -> None:
        pass


@dataclass
class DataSaveModeConfig(ActivableModeConfig):
    PATH            : str = ''

    def valid_check(self) -> None:
        pass


@dataclass
class MachineConfig:
    NAME                : str
    SENSORS             : List[str]
    FAULT_DETECTABLE    : bool
    FAULT_THRESHOLD     : int

    DATA_SEND_MODE      : DataSendModeConfig
    DATA_SAVE_MODE      : DataSaveModeConfig


@dataclass
class DAQSystemConfig:
    NI_DEVICES          : List[NIDeviceConfig]
    MACHINES            : List[MachineConfig]
