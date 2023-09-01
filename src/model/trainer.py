import os
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime
from keras.optimizers import Adam
from model.base_model import BaseModel
from model_config import ModelConfig
from sklearn.preprocessing import StandardScaler

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Trainer(BaseModel):
    def __init__(self, sensor_name: str, data_path: str):
        super(Trainer, self).__init__()
        self.seq_len = ModelConfig.SEQ_LEN
        self.latent_dim = ModelConfig.LATENT_DIM
        self.input_dim = ModelConfig.INPUT_DIM
        self.learning_rate = ModelConfig.LEARNING_RATE
        self.epoch = ModelConfig.EPOCH
        self.batch_size = ModelConfig.BATCH_SIZE
        self.threshold = ModelConfig.THRESHOLD

        self.scaler = StandardScaler()
        self.sensor_name = sensor_name
        self.data_path = data_path

    def _get_data(self):
        # 하루치 데이터 반환
        logger.info(f'센서 : {self.sensor_name}')

        for (root, directories, files) in os.walk(self.data_path):
            for file in files:
                df = pd.DataFrame()
                if '.csv' in file:
                    logger.info(f'파일 : {file}')
                    file_path = os.path.join(root, file)
                    df = pd.read_csv(file_path, names=['time', 'data'])
                df.dropna(axis=0, inplace=True)
                yield self._data_to_input(self.scaler.fit_transform(df)), df

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

        self.save_weights(f'{self.sensor_name}.h5')
        logger.info("모델 저장 완료")
        # 로드하기 전에 아래 코드 실행 필수
        # model.build((None, ModelConfig.SEQ_LEN, ModelConfig.INPUT_DIM))

        logger.info(f'로스 값 : {histories}')

        if plot_on:
            plt.plot(histories, label=self.sensor_name)
            plt.legend()
            plt.show()
        logger.info("학습 종료")
