import os
import pandas as pd
import asyncio

from model_config import TrainConfig, Config
from model.lstm_ae import LstmAE


def model_verifier(conf: TrainConfig) -> None:
    detected = []

    model = LstmAE(seq_len=conf.SEQ_LEN,
                   input_dim=conf.INPUT_DIM,
                   latent_dim=conf.LATENT_DIM,
                   batch_size=conf.BATCH_SIZE,
                   threshold=conf.THRESHOLD)
    model.load(model_path=f'{Config.MODEL_OUT}/{Config.NAME}/{conf.SENSOR_NAME}.h5')

    for file in os.listdir(Config.TEST_PATH):
        if f'{conf.SENSOR_NAME}.csv' in file:
            target = pd.read_csv(f'{Config.TEST_PATH}/{file}')
            target.drop(columns=['time'], axis=1, inplace=True)
            score = asyncio.run(model.detect(target, plot_on=False))

            if score != 0:
                print(f'file name : {file} score : {score}')
                detected.append({'file name : ': file, 'score : ': score})
                asyncio.run(model.detect(target, plot_on=True))

    print(detected)
