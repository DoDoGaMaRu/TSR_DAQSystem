import os
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import asyncio

from datetime import datetime
from keras.optimizers import Adam
from model.base_model import BaseModel
from model_config import TrainConfig, Config
from sklearn.preprocessing import StandardScaler


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Trainer(BaseModel):
    def __init__(self, conf: TrainConfig):
        self.seq_len = conf.SEQ_LEN
        self.latent_dim = conf.LATENT_DIM
        self.input_dim = conf.INPUT_DIM
        self.learning_rate = conf.LEARNING_RATE
        self.epoch = conf.EPOCH
        self.batch_size = conf.BATCH_SIZE
        self.threshold = conf.THRESHOLD

        super(Trainer, self).__init__(seq_len=self.seq_len,
                                      input_dim=self.input_dim,
                                      latent_dim=self.latent_dim)

        self.scaler = StandardScaler()
        self.sensor_name = conf.SENSOR_NAME
        self.data_path = Config.DATA_PATH

    def _get_data(self):
        # 하루치 데이터 반환
        logger.info(f'센서 : {self.sensor_name}')

        for file in os.listdir(self.data_path):
            if f'{self.sensor_name}.csv' in file:
                logger.info(f'파일 : {file}')
                file_path = os.path.join(self.data_path, file)
                df = pd.read_csv(file_path)
                df.drop(columns=['time'], axis=1, inplace=True)
                df.dropna(axis=0, inplace=True)

                yield asyncio.run(self._data_to_input(self.scaler.fit_transform(df))), df

    def data_plot(self):
        for file in os.listdir(self.data_path):
            if f'{self.sensor_name}.csv' in file:
                target = pd.read_csv(f'{self.data_path}/{file}')
                target.drop(columns=['time'], axis=1, inplace=True)
                plt.plot(target, label=f'{file}')
                plt.legend()
                plt.show()

    def train(self, gpu_on: bool = True, plot_on: bool = True):
        if gpu_on:
            os.environ['CUDA_VISIBLE_DEVICES'] = '0'
        else:
            os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

        logger.info("학습 시작")
        learning_rate = self.learning_rate
        optimizer = Adam(learning_rate=learning_rate)
        self.compile(optimizer=optimizer, loss='mse')

        histories = []
        for i in range(self.epoch):
            cur_history = []
            for data, _ in self._get_data():
                history = self.fit(x=data,
                                   y=data,
                                   batch_size=self.batch_size,
                                   epochs=1,
                                   verbose=1,
                                   workers=4)
                logger.info("학습 완료")
                cur_history.append(history.history['loss'])
            histories.append(np.mean(cur_history))
            logger.info(f"{datetime.now()} epoch : {i + 1}/{self.epoch}, loss : {np.mean(cur_history)}")

        _init_dirs(f'{Config.MODEL_OUT}/{Config.NAME}')
        self.save_weights(f'{Config.MODEL_OUT}/{Config.NAME}/{self.sensor_name}.h5')
        logger.info("모델 저장 완료")
        logger.info(f'로스 값 : {histories}')

        if plot_on:
            plt.plot(histories, label=self.sensor_name)
            plt.legend()
            plt.show()
        logger.info("학습 종료")


def _init_dirs(directory):
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except:
            pass