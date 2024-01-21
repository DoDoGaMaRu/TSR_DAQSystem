import asyncio
from typing import List
from PySide6.QtCore import QThread

from lib.daq import DAQ
from lib.daq.ni_device import NIDevice
from lib.daq.ni_device.channel_initializers import VibChannelInitializer, TempChannelInitializer

from config import NIDeviceConfig, NIDeviceType, DAQSystemConfig, MachineConfig
from .data_saver import DataSaver
from .data_sender import DataSender
from .machine import Machine


class DAQSystem(QThread):
    def __init__(self, conf: DAQSystemConfig):
        super().__init__()
        self._loop = asyncio.get_event_loop()
        self._ni_devices: List[NIDevice] = [create_ni_device(ni_conf) for ni_conf in conf.NI_DEVICES]
        self._machines: List[Machine] = [create_machine(m_conf) for m_conf in conf.MACHINES]

        self._daq: DAQ = DAQ(ni_devices=self._ni_devices)
        for machine in self._machines:
            self._daq.register_data_handler(machine)

    def get_machines(self):
        return self._machines

    def run(self) -> None:
        self._daq.read_start()
        self._loop.run_forever()


def create_ni_device(conf: NIDeviceConfig) -> NIDevice:
    device_type = conf.TYPE
    channel_initializer = None

    if device_type == NIDeviceType.VIB:
        channel_initializer = VibChannelInitializer()
    elif device_type == NIDeviceType.TEMP:
        channel_initializer = TempChannelInitializer()
    else:
        RuntimeError('invalid device type')

    ni_device = NIDevice(name=conf.NAME,
                         rate=conf.RATE,
                         channel_initializer=channel_initializer)

    for s_conf in conf.SENSORS:
        ni_device.add_sensor(sensor_name=s_conf.NAME,
                             channel=s_conf.CHANNEL,
                             options=s_conf.OPTIONS)

    return ni_device


def create_machine(conf: MachineConfig) -> Machine:
    machine = Machine(name=conf.NAME,
                      sensors=conf.SENSORS,
                      fault_detectable=conf.FAULT_DETECTABLE,
                      fault_threshold=conf.FAULT_THRESHOLD)

    send_conf = conf.DATA_SEND_MODE
    if send_conf.ACTIVATE:
        data_sender = DataSender(name=conf.NAME,
                                 host=send_conf.HOST,
                                 port=send_conf.PORT,
                                 timeout=send_conf.TIMEOUT)
        machine.register_handler(data_sender)

    save_conf = conf.DATA_SAVE_MODE
    if save_conf.ACTIVATE:
        data_saver = DataSaver(name=conf.NAME,
                               sensors=conf.SENSORS,
                               external_path=save_conf.PATH)
        machine.register_handler(data_saver)

    return machine
