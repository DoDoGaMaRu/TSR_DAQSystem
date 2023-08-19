import os

import keras.models
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging

from keras.optimizers import Adam
from keras.models import Model
from keras.layers import LSTM, RepeatVector, TimeDistributed, Dense
from sklearn.model_selection import train_test_split
from config import ModelConfig, SensorConfig
from tqdm import tqdm

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

        self.train_input = None
        self.test_input = None

    def call(self, inputs, training=None, mask=None):
        z, z_rep = self.encoder(inputs)
        decoded = self.decoder(z_rep)

        return decoded

    def _get_data(self, data_path: str) -> tuple:
        logger.info("데이터 추출 중")
        columns = [channel_name for device_config in SensorConfig.DEVICES for channel_name in device_config.CHANNEL_NAMES]

        df = pd.DataFrame()
        for column in tqdm(columns):
            for (root, directories, files) in os.walk(f'{data_path}/{column}'):
                for file in files:
                    if '.csv' in file:
                        file_path = os.path.join(root, file)
                        cur_df = pd.read_csv(file_path, names=['time', column])
                        df[column] = cur_df[column]

        train, test = train_test_split(df, test_size=self.test_size, shuffle=False)
        return train, test

    def _data_to_input(self, data: tuple) -> None:
        # LSTM의 입력 데이터로 변환하는 메소드
        # (입력 데이터 수, 시퀀스 길이, 사용할 컬럼 수)의 형태가 되어야 함
        train_list = []
        test_list = []
        train, test = data

        logger.info("훈련 데이터 변환 중")
        #for i in tqdm(range(len(train) - self.seq_len)):
        #    train_list.append(train.iloc[i:(i + self.seq_len)].values)
        logger.info("시험 데이터 변환 중")
        for i in tqdm(range(len(test) - self.seq_len)):
            test_list.append(test.iloc[i:(i + self.seq_len)].values)

        self.train_input = np.array(train_list)
        self.test_input = np.array(test_list)

    def train(self, data_path: str):
        logger.info("학습 시작")
        data = self._get_data(data_path)
        self._data_to_input(data)

        # specify learning rate
        learning_rate = self.learning_rate
        # create an Adam optimizer with the specified learning rate
        optimizer = Adam(learning_rate=learning_rate)

        self.compile(optimizer=optimizer, loss='mse')

        # train
        history = self.fit(self.test_input, self.test_input, epochs=1, batch_size=5, validation_split=0.1, verbose=1)

        # save weights
        self.save_weights("lstm_ae.h5")
        logger.info("모델 저장 완료")

        # plotting
        plt.plot(history.history['loss'], label='Training loss')
        plt.plot(history.history['val_loss'], label='Validation loss')
        plt.legend()
        plt.show()
        logger.info("학습 종료")
