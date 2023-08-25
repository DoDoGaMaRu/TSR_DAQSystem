import os
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

from keras.optimizers import Adam
from keras.models import Model
from keras.layers import LSTM, RepeatVector, TimeDistributed, Dense
from sklearn.preprocessing import StandardScaler
from pandas import DataFrame
from config import ModelConfig, SensorConfig
from tqdm import tqdm

os.environ['CUDA_VISIBLE_DEVICES'] = '0'
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Encoder(Model):
    def __init__(self, seq_length, latent_dim):
        super(Encoder, self).__init__()

        self.h1 = LSTM(128, return_sequences=True)
        self.h2 = LSTM(latent_dim, return_sequences=False)
        self.h3 = RepeatVector(seq_length)

    def call(self, inputs, training=None, mask=None):
        x = self.h1(inputs, training=training, mask=mask)
        z = self.h2(x, training=training, mask=mask)
        z_rep = self.h3(z)

        return z, z_rep


class Decoder(Model):
    def __init__(self, input_dim, latent_dim):
        super(Decoder, self).__init__()

        self.h1 = LSTM(latent_dim, return_sequences=True)
        self.h2 = LSTM(128, return_sequences=True)
        self.h3 = TimeDistributed(Dense(input_dim))

    def call(self, inputs, training=None, mask=None):
        x = self.h1(inputs, training=training, mask=mask)
        x = self.h2(x, training=training, mask=mask)
        x = self.h3(x, training=training, mask=mask)

        return x


class LstmAE(Model):
    def __init__(self):
        super(LstmAE, self).__init__()
        self.encoder = Encoder(ModelConfig.SEQ_LEN, ModelConfig.LATENT_DIM)
        self.decoder = Decoder(ModelConfig.INPUT_DIM, ModelConfig.LATENT_DIM)

        self.seq_len = ModelConfig.SEQ_LEN
        self.latent_dim = ModelConfig.LATENT_DIM
        self.input_dim = ModelConfig.INPUT_DIM
        self.learning_rate = ModelConfig.LEARNING_RATE
        self.epoch = ModelConfig.EPOCH
        self.batch_size = ModelConfig.BATCH_SIZE

        self.scaler = StandardScaler()

    def call(self, inputs, training=None, mask=None):
        z, z_rep = self.encoder(inputs)
        decoded = self.decoder(z_rep)

        return decoded

    def _get_data(self, data_path: str):
        # 하루치 데이터 반환
        columns = [channel_name for device_config in SensorConfig.DEVICES for channel_name in device_config.CHANNEL_NAMES]
        logger.info(f'식별된 센서 : {columns}')

        file_count = 10000000
        logger.info('파일 개수 찾는 중')
        for column in tqdm(columns):
            cur_file_count = 0
            for (root, directories, files) in os.walk(f'{data_path}/{column}'):
                for file in files:
                    if '.csv' in file:
                        cur_file_count = cur_file_count + 1
            file_count = min(file_count, cur_file_count)
        logger.info(f'파일 개수 : {file_count}')

        df = pd.DataFrame()
        for idx in range(file_count):
            for column in columns:
                sensor_df = pd.DataFrame()
                for (root, directories, files) in os.walk(f'{data_path}/{column}'):
                    file = files[idx]
                    if '.csv' in file:
                        logger.info(f'{idx + 1}번째 파일, {file}')
                        file_path = os.path.join(root, file)
                        cur_df = pd.read_csv(file_path, names=['time', column])
                        sensor_df[column] = cur_df[column]
                df[column] = sensor_df[column]

            yield self._data_to_input(self.scaler.fit_transform(df))

    def _data_to_input(self, data: list) -> object:
        # LSTM의 입력 데이터로 변환하는 메소드
        # (입력 데이터 수, 시퀀스 길이, 사용할 컬럼 수)의 형태가 되어야 함
        data_list = []

        logger.info("데이터 변환중")
        for i in tqdm(range(len(data) - self.seq_len)):
            data_list.append(data[i:(i + self.seq_len)])

        return np.array(data_list)

    def train(self, data_path: str):
        logger.info("학습 시작")
        learning_rate = self.learning_rate
        optimizer = Adam(learning_rate=learning_rate)
        self.compile(optimizer=optimizer, loss='mse')

        histories = []
        for i in range(self.epoch):
            cur_history = []
            for data in self._get_data(data_path):
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

        self.save_weights("lstm_ae.h5")
        logger.info("모델 저장 완료")
        # 로드하기 전에 아래 코드 실행 필수
        # model.build((None, ModelConfig.SEQ_LEN, ModelConfig.INPUT_DIM))

        plt.plot(histories)
        plt.legend()
        plt.show()
        logger.info("학습 종료")

    def validate(self, data_path: str):
        logger.info("검증 시작")
        for data in self._get_data(data_path):
            print(data)
            logger.info(self.predict(data))
            break
