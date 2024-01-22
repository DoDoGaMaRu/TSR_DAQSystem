import nidaqmx
import nidaqmx.constants
from scipy import signal
from typing import List, Dict

from .channel_initializers import ChannelInitializer

MIN_RATE: int = 3000


class NIDevice:
    def __init__(self,
                 name,
                 rate,
                 channel_initializer: ChannelInitializer):
        self._name: str = name
        self._rate: int = rate
        self._real_rate: int = rate if rate > MIN_RATE else MIN_RATE
        self._sensor_names: List[str] = []
        self._is_single_channel = False

        self._task = nidaqmx.Task()
        self._channel_initializer = channel_initializer

    def _set_timing(self, rate: int, samples_per_channel: int) -> None:
        self._task.timing.cfg_samp_clk_timing(rate=rate,
                                              active_edge=nidaqmx.constants.Edge.RISING,
                                              sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,
                                              samps_per_chan=samples_per_channel)

    def add_sensor(self, sensor_name, channel, options: Dict[str, any]) -> None:
        physical_channel = f'{self._name}/{channel}'
        self._channel_initializer.add_channel(self._task, physical_channel, **options)

        self._sensor_names.append(sensor_name)
        self._is_single_channel = len(self._sensor_names) == 1

        self._set_timing(rate=self._real_rate,
                         samples_per_channel=self._real_rate*2)

    async def read(self) -> Dict[str, List[float]]:
        data_list = self._task.read(number_of_samples_per_channel=self._real_rate)
        data_list = [data_list] if self._is_single_channel else data_list
        data_list = [signal.resample(data, self._rate).tolist() for data in data_list]
        named_datas = dict(zip(self._sensor_names, data_list))
        return named_datas

    def name(self) -> str:
        return self._name
