import asyncio

from typing import List

import nidaqmx.errors

from config import ClientConfig, SensorConfig
from network import TCPClient
from daq import Sensor, SensorType, DeviceConf
from sensorHandler import SensorHandler


def tcp_client_load() -> TCPClient:
    tcp_client = TCPClient(host=ClientConfig.HOST,
                           port=ClientConfig.PORT,
                           name=ClientConfig.MACHINE_NAME,
                           timeout=ClientConfig.TIMEOUT)
    return tcp_client


def sensor_handler_load(tcp_client: TCPClient) -> List[SensorHandler]:
    sensor_handlers = []
    for devices_conf in SensorConfig.DEVICES:
        conf = DeviceConf(sensor_type=SensorType.__members__[devices_conf.TYPE],
                          channel=f"{devices_conf.NAME}/{devices_conf.CHANNEL}")
        sensor = Sensor.of(name=f'{devices_conf.TYPE}:{devices_conf.NAME}',
                           device_conf=conf,
                           rate=SensorConfig.RATE,
                           samples_per_channel=SensorConfig.RATE*2)
        sensor_handler = SensorHandler(sensor=sensor,
                                       resampling_rate=SensorConfig.NUMBER_OF_SAMPLES,
                                       channel_names=devices_conf.CHANNEL_NAMES,
                                       tcp_client=tcp_client)
        sensor_handlers.append(sensor_handler)
    return sensor_handlers


async def sensor_read_loop(sensor_handler: SensorHandler):
    while True:
        try:
            await sensor_handler.read()
        except nidaqmx.errors.DaqReadError:
            pass
        except Exception as err:
            print(f'정의되지 않은 오류\n{str(err)}')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    tcp_client = tcp_client_load()
    sensor_handlers = sensor_handler_load(tcp_client)
    for handler in sensor_handlers:
        loop.create_task(sensor_read_loop(handler))

    loop.run_until_complete(tcp_client.permanent_connection())
