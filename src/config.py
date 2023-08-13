import configparser

config_file = 'resources/config.ini'
cfg = configparser.ConfigParser()
cfg.read(config_file)


class ClientConfig:
    HOST: str = cfg['CLIENT']['HOST']
    PORT: int = cfg['CLIENT']['PORT']
    MACHINE_NAME: str = cfg['CLIENT']['MACHINE_NAME']
    TIMEOUT: int = cfg['CLIENT']['TIMEOUT']


class SensorConfig:
    RATE: int = cfg['SENSOR']['RATE'] if int(cfg['SENSOR']['RATE']) > 2500 else 2500
    NUMBER_OF_SAMPLES = cfg['SENSOR']['RATE']
    MIN_SAMPLING_RATE = 2400
    READ_COUNT: int = cfg['SENSOR']['READ_COUNT']
    READ_TIMEOUT: int = cfg['SENSOR']['READ_TIMEOUT']
    DEVICES: list = cfg['SENSOR']['DEVICES']
