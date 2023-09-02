import os
import pandas as pd
import asyncio

from model.lstm_ae import LstmAE
from model_config import ModelConfig


def model_verifier(model_path: str, data_path: str) -> None:
    detected = []

    model = LstmAE(seq_len=ModelConfig.SEQ_LEN,
                   input_dim=ModelConfig.INPUT_DIM,
                   latent_dim=ModelConfig.LATENT_DIM,
                   batch_size=ModelConfig.BATCH_SIZE,
                   threshold=ModelConfig.THRESHOLD)
    model.load(model_path=model_path)

    for (root, directories, files) in os.walk(data_path):
        for file in files:
            if '.csv' in file:
                target = pd.read_csv(f'{data_path}/{file}', names=['time', 'data'])
                target.drop(columns=['time'], axis=1, inplace=True)
                score = asyncio.run(model.detect(target, plot_on=False))

                if score != 0:
                    print(f'file name : {file} score : {score}')
                    detected.append({'file name : ': file, 'score : ': score})
                    asyncio.run(model.detect(target, plot_on=True))

    print(detected)
