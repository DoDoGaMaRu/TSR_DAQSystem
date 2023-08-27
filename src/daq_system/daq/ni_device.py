import nidaqmx
import nidaqmx.system
import nidaqmx.constants

from nidaqmx.constants import RTDType, ResistanceConfiguration, ExcitationSource
from enum import Enum, auto
from scipy import signal
from typing import List
from dataclasses import dataclass


MIN_RATE: int = 2400


class DeviceType(Enum):
    VIB: int = auto()
    TEMP: int = auto()


@dataclass
class DeviceConfig:
    NAME            : str
    TYPE            : DeviceType
    RATE            : int
    CHANNELS        : List[str]
    CHANNEL_NAMES   : List[str]

    def __post_init__(self):
        if len(self.CHANNELS) < 1 or len(self.CHANNELS) != len(self.CHANNEL_NAMES):
            raise ValueError('Wrong conf')
        if isinstance(self.TYPE, str):
            self.TYPE = DeviceType.__members__[self.TYPE]


class NIDevice:
    def __init__(self, conf: DeviceConfig):
        self.name = conf.NAME
        self.device_type = conf.TYPE
        self.rate = conf.RATE
        self.real_rate = conf.RATE if conf.RATE > MIN_RATE else MIN_RATE
        self.channel_names = conf.CHANNEL_NAMES
        self.is_single_channel = len(conf.CHANNELS) == 1

        self.task = nidaqmx.Task()
        for channel in conf.CHANNELS:
            self._add_channel(channel)
        self._set_timing(rate=self.real_rate,
                         samples_per_channel=self.real_rate*2)

    def _add_channel(self, channel: str):
        channel = f'{self.name}/{channel}'
        if self.device_type == DeviceType.VIB:
            self._add_vib_channel(channel)
        elif self.device_type == DeviceType.TEMP:
            self._add_temp_channel(channel)

    def _add_vib_channel(self, channel: str):
        self.task.ai_channels.add_ai_voltage_chan(channel)

    def _add_temp_channel(self, channel: str):
        self.task.ai_channels.add_ai_rtd_chan(channel, min_val=0.0, max_val=100.0, rtd_type=RTDType.PT_3750,
                                              resistance_config=ResistanceConfiguration.THREE_WIRE,
                                              current_excit_source=ExcitationSource.INTERNAL, current_excit_val=0.00100)

    def _set_timing(self, rate: int, samples_per_channel: int):
        self.task.timing.cfg_samp_clk_timing(rate=rate,
                                             active_edge=nidaqmx.constants.Edge.RISING,
                                             sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,
                                             samps_per_chan=samples_per_channel)

    async def read(self):
        data_list = self.task.read(number_of_samples_per_channel=self.real_rate)
        data_list = [data_list] if self.is_single_channel else data_list
        data_list = [signal.resample(data, self.rate).tolist() for data in data_list]
        named_datas = dict(zip(self.channel_names, data_list))
        return named_datas
