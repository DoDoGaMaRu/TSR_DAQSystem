import shutil
import yaml
from model.trainer import Trainer
from model.verifier import model_verifier
from model_config import Config
# CUDA 사용을 위해서는 tensorflow-gpu==2.10.0 라이브러리를 사용해야합니다.


def make_tar():
    target = f"{Config.MODEL_OUT}/{Config.NAME}/"
    tar_path = f"{Config.MODEL_OUT}/{Config.NAME}"

    shutil.make_archive(tar_path, 'tar', target)
    shutil.rmtree(tar_path)


def save_metadata():
    metadata = {
        'NAME': Config.NAME,
        'MODELS': [
            {
                'NAME': conf.SENSOR_NAME,
                'SEQ_LEN': conf.SEQ_LEN,
                'LATENT_DIM': conf.LATENT_DIM,
                'BATCH_SIZE': conf.BATCH_SIZE,
                'THRESHOLD': conf.THRESHOLD
            }
            for conf in Config.TRAIN
        ]
    }
    meta_path = f"{Config.MODEL_OUT}/{Config.NAME}/METADATA.yml"
    with open(meta_path, 'w', encoding='UTF-8') as limit_yml:
        yaml.dump(metadata, limit_yml, default_flow_style=False)


if __name__ == '__main__':
    for conf in Config.TRAIN:
        trainer = Trainer(conf=conf)
        trainer.data_plot()
        trainer.train()
        model_verifier(conf=conf)
    save_metadata()
    make_tar()
