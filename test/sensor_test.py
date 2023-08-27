import time
import asyncio
from last.daq import Sensor, SensorType, DeviceConf


vib_channel = 'vib/ai0:3'
temp_channel = 'temp/ai0:1'
rate = 2400

loop = asyncio.get_event_loop()
vib_conf = DeviceConf(sensor_type=SensorType.VIB,
                      channel=vib_channel)

vib_sensor = Sensor.of(name='temp', device_conf=vib_conf, rate=rate, samples_per_channel=rate * 2)


temp_conf = DeviceConf(sensor_type=SensorType.TEMP,
                       channel=temp_channel)
temp_sensor = Sensor.of(name='vib', device_conf=temp_conf, rate=rate, samples_per_channel=rate * 2)


async def read_loop():
    while True:
        start = time.time()
        data = await temp_sensor.read()
        print(len(data[0]))
        await asyncio.sleep(1)
        end = time.time()
        print(f"{end - start:.5f} sec")
        print()

loop.run_until_complete(read_loop())
