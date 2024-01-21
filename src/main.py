from app import App
from config import *


def temp_config() -> DAQSystemConfig:
    ni_device_confs = [
        NIDeviceConfig(
            NAME='vib',
            TYPE=NIDeviceType.VIB,
            RATE=300,
            SENSORS=[
                SensorConfig(NAME='shot_blast_vib', CHANNEL='ai0', OPTIONS={}),
                SensorConfig(NAME='aro_vib1', CHANNEL='ai1', OPTIONS={'sensitivity': 100}),
                SensorConfig(NAME='aro_vib2', CHANNEL='ai2', OPTIONS={}),
                SensorConfig(NAME='dispensing_vib', CHANNEL='ai3', OPTIONS={}),
            ]
        )
    ]
    machine_confs = [
        MachineConfig(
            NAME='AROPump',
            SENSORS=['aro_vib1', 'aro_vib2'],
            FAULT_DETECTABLE=False,
            FAULT_THRESHOLD=0,
            DATA_SAVE_MODE=DataSaveModeConfig(
                ACTIVATE=True,
                PATH='C://Users//DaeHwan//Desktop'
            ),
            DATA_SEND_MODE=DataSendModeConfig(
                ACTIVATE=False
            )
        ),
        MachineConfig(
            NAME='ShotBlast',
            SENSORS=['shot_blast_vib'],
            FAULT_DETECTABLE=False,
            FAULT_THRESHOLD=0,
            DATA_SAVE_MODE=DataSaveModeConfig(
                ACTIVATE=True,
                PATH='C://Users//DaeHwan//Desktop'
            ),
            DATA_SEND_MODE=DataSendModeConfig(
                ACTIVATE=False
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
