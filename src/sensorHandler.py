import asyncio
from time import ctime, time
from typing import List

from controllers.rawdataController import RawdataController
from daq import Sensor
from network import TCPClient
from scipy import signal


class SensorHandler:
    def __init__(self,
                 sensor: Sensor,
                 channel_names: List[str],
                 tcp_client: TCPClient,
                 resampling_rate: int):
        self.sensor = sensor
        self.resampling_rate = resampling_rate
        self.channel_names = channel_names
        self.tcp_client = tcp_client
        self.rdc = RawdataController()
        self.is_single_channel = len(channel_names) == 1

    async def read(self):
        now_time = ctime(time())
        data_list = await self.sensor.read()
        if self.is_single_channel:
            data_list = [data_list]

        data_list = [signal.resample(data, self.resampling_rate).tolist() for data in data_list]
        message = _get_sensor_message(now_time, self.channel_names, data_list)

        await asyncio.sleep(1)
        await self.rdc.add_data(self.sensor.name, message)
        if not self.tcp_client.is_closing():
            self.tcp_client.send_data(event=self.sensor.name, data=message)
            print('data send')


def _get_sensor_message(time_, channel_names, data_list):
    message = {
        'time': time_
    }
    for idx, data in enumerate(data_list):
        message[channel_names[idx]] = data

    return message
