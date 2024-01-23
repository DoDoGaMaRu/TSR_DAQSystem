from app import App
from config import *


def temp_config() -> DAQSystemConfig:
    ni_device_confs = [
        NIDeviceConfig(
            NAME='temp_device1',
            TYPE=NIDeviceType.TEMP,
            RATE=20,
            SENSORS=[
                SensorConfig(NAME='t1', CHANNEL='ai0', OPTIONS={}),
                SensorConfig(NAME='t2', CHANNEL='ai1', OPTIONS={}),
                SensorConfig(NAME='t3', CHANNEL='ai2', OPTIONS={}),
                SensorConfig(NAME='t4', CHANNEL='ai3', OPTIONS={}),
            ]
        ),
        NIDeviceConfig(
            NAME='vib_device1',
            TYPE=NIDeviceType.VIB,
            RATE=30,
            SENSORS=[
                SensorConfig(NAME='shot_blast_vib', CHANNEL='ai0', OPTIONS={'sensitivity': 100}),
                SensorConfig(NAME='aro_vib1', CHANNEL='ai1', OPTIONS={'sensitivity': 100}),
                SensorConfig(NAME='aro_vib2', CHANNEL='ai2', OPTIONS={'sensitivity': 100}),
                SensorConfig(NAME='dispensing_vib', CHANNEL='ai3', OPTIONS={'sensitivity': 100}),
            ]
        ),
        NIDeviceConfig(
            NAME='vib_device2',
            TYPE=NIDeviceType.VIB,
            RATE=30,
            SENSORS=[
                SensorConfig(NAME='v1', CHANNEL='ai0', OPTIONS={'sensitivity': 100}),
                SensorConfig(NAME='v2', CHANNEL='ai1', OPTIONS={'sensitivity': 100}),
                SensorConfig(NAME='v3', CHANNEL='ai2', OPTIONS={'sensitivity': 100}),
                SensorConfig(NAME='v4', CHANNEL='ai3', OPTIONS={'sensitivity': 100}),
            ]
        )
    ]
    machine_confs = [
        MachineConfig(
            NAME='AROPump',
            SENSORS=['aro_vib1', 'aro_vib2'],
            FAULT_DETECTABLE=True,
            FAULT_THRESHOLD=10,
            DATA_SAVE_MODE=DataSaveModeConfig(
                ACTIVATION=True,
                PATH='C://Users//DaeHwan//Desktop//data'
            ),
            DATA_SEND_MODE=DataSendModeConfig(
                ACTIVATION=True,
                HOST='192.168.0.21',
                PORT=8082,
                TIMEOUT=60
            )
        ),
        MachineConfig(
            NAME='ShotBlast',
            SENSORS=['shot_blast_vib'],
            FAULT_DETECTABLE=False,
            FAULT_THRESHOLD=0,
            DATA_SAVE_MODE=DataSaveModeConfig(
                ACTIVATION=False,
                PATH='C://Users//DaeHwan//Desktop//data'
            ),
            DATA_SEND_MODE=DataSendModeConfig(
                ACTIVATION=True,
                HOST='192.168.0.21',
                PORT=8082,
                TIMEOUT=60
            )
        )
    ]

    daq_conf = DAQSystemConfig(NI_DEVICES=ni_device_confs,
                               MACHINES=machine_confs)

    return daq_conf


if __name__ == '__main__':
    ConfigLoader.save_conf(temp_config())
    app = App()
    app.run()
