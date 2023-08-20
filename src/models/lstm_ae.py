import os
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from keras.optimizers import Adam
from keras.models import Model
from keras.layers import LSTM, RepeatVector, TimeDistributed, Dense
from sklearn.model_selection import train_test_split
from config import ModelConfig, SensorConfig

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Encoder(Model):
    def __init__(self, seq_length, latent_dim):
        super(Encoder, self).__init__()

        self.h1 = LSTM(128, return_sequences=True)  # (seq_len, input_dim) -> (seq_len, 128))
        self.h2 = LSTM(latent_dim, return_sequences=False) # (seq_len , 128) -> (latent_dim)
        self.h3 = RepeatVector(seq_length) # (latent_dim) -> (seq_length, latent_dim)

    def call(self, inputs, training=None, mask=None):
        x = self.h1(inputs, training=training, mask=mask)
        z = self.h2(x, training=training, mask=mask)
        z_rep = self.h3(z)

        return z, z_rep


class Decoder(Model):
    def __init__(self, input_dim, latent_dim):
        super(Decoder, self).__init__()

        self.h1 = LSTM(latent_dim, return_sequences=True) # (seq_length, latent_dim) -> (seq_len, input_dim)
        self.h2 = LSTM(128, return_sequences=True) # (seq_len, input_dim) -> (seq_length, 128)
        self.h3 = TimeDistributed(Dense(input_dim)) # (seq_length, 128) -> (seq_length, input_dim)

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
        self.test_size = ModelConfig.TEST_SIZE
        self.learning_rate = ModelConfig.LEARNING_RATE
        self.epoch = ModelConfig.EPOCH
        self.batch_size = ModelConfig.BATCH_SIZE

    def call(self, inputs, training=None, mask=None):
        z, z_rep = self.encoder(inputs)
        decoded = self.decoder(z_rep)

        return decoded

    def _get_data(self, data_path: str) -> tuple:
        # 하루치 데이터 반환
        columns = [channel_name for device_config in SensorConfig.DEVICES for channel_name in device_config.CHANNEL_NAMES]

        file_count = 10000000
        for column in columns:
            cur_file_count = 0
            for (root, directories, files) in os.walk(f'{data_path}/{column}'):
                for file in files:
                    if '.csv' in file:
                        cur_file_count = cur_file_count + 1
            file_count = min(file_count, cur_file_count)

        df = pd.DataFrame()
        for idx in range(file_count):
            for column in columns:
                sensor_df = pd.DataFrame()
                for (root, directories, files) in os.walk(f'{data_path}/{column}'):
                    file = files[idx]
                    if '.csv' in file:
                        file_path = os.path.join(root, file)
                        cur_df = pd.read_csv(file_path, names=['time', column])
                        sensor_df[column] = cur_df[column]
                df[column] = sensor_df[column]

            data = train_test_split(df, test_size=self.test_size, shuffle=False)
            yield self._data_to_input(data)

    def _data_to_input(self, data: tuple) -> tuple:
        # LSTM의 입력 데이터로 변환하는 메소드
        # (입력 데이터 수, 시퀀스 길이, 사용할 컬럼 수)의 형태가 되어야 함
        train_list = []
        test_list = []
        train, test = data

#        for i in range(len(train) - self.seq_len):
#            train_list.append(train.iloc[i:(i + self.seq_len)].values)
        for i in range(len(test) - self.seq_len):
            test_list.append(test.iloc[i:(i + self.seq_len)].values)

        return np.array(train_list), np.array(test_list)

    def train(self, data_path: str):
        logger.info("학습 시작")
        learning_rate = self.learning_rate
        optimizer = Adam(learning_rate=learning_rate)
        self.compile(optimizer=optimizer, loss='mse')

        histories = []
        for i in range(self.epoch):
            cur_history = []
            for train, test in self._get_data(data_path):
                history = self.fit(x=test,
                                   y=test,
                                   batch_size=self.batch_size,
                                   epochs=1,
                                   verbose=0)
                cur_history.append(history.history['loss'])
            histories.append(np.mean(cur_history))
            logger.info(f"epoch : {i + 1}/{self.epoch}, loss : {np.mean(cur_history)}")

        # save weights
        self.save_weights("lstm_ae.h5")
        logger.info("모델 저장 완료")
        # 로드하기 전에 아래 코드 실행 필수
        # model.build((None, ModelConfig.SEQ_LEN, ModelConfig.INPUT_DIM))

        # plotting
        plt.plot(histories)
        plt.legend()
        plt.show()
        logger.info("학습 종료")
