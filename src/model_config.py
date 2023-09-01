import yaml

config_file = '../src/resources/model_config.yml'
with open(config_file, 'r', encoding='UTF-8') as yml:
    cfg = yaml.safe_load(yml)


class ModelConfig:
    SEQ_LEN             : int = cfg['MODEL']['SEQ_LEN']
    LATENT_DIM          : int = cfg['MODEL']['LATENT_DIM']
    INPUT_DIM           : int = 1
    LEARNING_RATE       : float = cfg['MODEL']['LEARNING_RATE']
    EPOCH               : int = cfg['MODEL']['EPOCH']
    BATCH_SIZE          : int = cfg['MODEL']['BATCH_SIZE'] - SEQ_LEN
    THRESHOLD           : float = cfg['MODEL']['THRESHOLD']

# TODO 실제로는 모델별로 컨픽이 여러개 있을 것이므로 수정
