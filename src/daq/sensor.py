import nidaqmx
import nidaqmx.system
import nidaqmx.constants

from nidaqmx.constants import *
from enum import Enum, auto
from typing import Union, List
from dataclasses import dataclass


class SensorType(Enum):
    VIB: int = auto()
    TEMP: int = auto()


@dataclass
class SensorConf:
    sensor_type: SensorType = None
    channel: str = None


class Sensor:
    def __init__(self):
        self.task = nidaqmx.Task()
        self.read_count = 1

    def _add_sensor(self, channel: SensorConf):
        if channel.sensor_type == SensorType.VIB:
            self._add_vib_channel(channel.channel)
        elif channel.sensor_type == SensorType.TEMP:
            self._add_temp_channel(channel.channel)

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

    def _set_sample_count(self, count: int):
        self.read_count = count

    async def read(self):
        return self.task.read(number_of_samples_per_channel=self.read_count, timeout=10.0)

    @classmethod
    def of(cls, sensor_conf: Union[SensorConf, List[SensorConf]], rate: int, samples_per_channel: int):
        instance = cls()

        if isinstance(sensor_conf, SensorConf):
            instance._add_sensor(sensor_conf)
            instance._set_timing(rate, samples_per_channel)
            instance._set_sample_count(rate)

        elif isinstance(sensor_conf, List):
            for s in sensor_conf:
                instance._add_sensor(s)
            instance._set_timing(rate, samples_per_channel)

        return instance
