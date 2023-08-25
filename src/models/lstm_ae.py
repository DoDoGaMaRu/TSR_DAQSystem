import os
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
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
        self.threshold = ModelConfig.THRESHOLD

        self.scaler = StandardScaler()
        self.columns = [channel_name for device_config in SensorConfig.DEVICES for channel_name in device_config.CHANNEL_NAMES]

    def call(self, inputs, training=None, mask=None):
        z, z_rep = self.encoder(inputs)
        decoded = self.decoder(z_rep)

        return decoded

    def _get_data(self, data_path: str):
        # 하루치 데이터 반환
        logger.info(f'식별된 센서 : {self.columns}')

        file_count = 10000000
        logger.info('파일 개수 찾는 중')
        for column in tqdm(self.columns):
            cur_file_count = 0
            for (root, directories, files) in os.walk(f'{data_path}/{column}'):
                for file in files:
                    if '.csv' in file:
                        cur_file_count = cur_file_count + 1
            file_count = min(file_count, cur_file_count)
        logger.info(f'파일 개수 : {file_count}')

        df = pd.DataFrame()
        for idx in range(file_count):
            for column in self.columns:
                sensor_df = pd.DataFrame()
                for (root, directories, files) in os.walk(f'{data_path}/{column}'):
                    file = files[idx]
                    if '.csv' in file:
                        logger.info(f'{idx + 1}번째 파일, {file}')
                        file_path = os.path.join(root, file)
                        cur_df = pd.read_csv(file_path, names=['time', column])
                        sensor_df[column] = cur_df[column]
                df[column] = sensor_df[column]

            yield self._data_to_input(self.scaler.fit_transform(df)), df

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
            for data, _ in self._get_data(data_path):
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

    def eval(self, data_path: str):
        for data, raw_data in self._get_data(data_path):
            train_predict = self.predict(data)
            train_mae = np.mean(np.abs(train_predict - data), axis=1)

            plt.plot(train_mae)
            plt.show()

            for sensor_idx in range(ModelConfig.INPUT_DIM):
                predicted_sensor = train_predict[:, -1, sensor_idx].reshape(-1, 1)
                predicted_sensor = self.scaler.inverse_transform(predicted_sensor)

                plt.figure(figsize=(12, 6))
                plt.plot(raw_data.index,
                         self.scaler.inverse_transform(raw_data[self.columns[sensor_idx]].values.reshape(-1, 1)),
                         color='blue',
                         label='raw data')
                plt.legend()
                plt.show()

                plt.figure(figsize=(12, 6))
                plt.plot(raw_data.index[len(raw_data.index) - len(predicted_sensor):],
                         predicted_sensor,
                         color='red',
                         label='predicted data')
                plt.legend()
                plt.show()

    def detect(self, target: DataFrame):
        target_input = self._data_to_input(self.scaler.fit_transform(target))
        target_predict = self.predict(target_input)
        target_mae = np.mean(np.abs(target_predict - target_input), axis=1)

        plt.plot(target_mae)
        plt.show()

        for sensor_idx in range(ModelConfig.INPUT_DIM):
            predicted_sensor = self.scaler.inverse_transform(target_predict[:, -1, sensor_idx].reshape(-1, 1))

            plt.figure(figsize=(12, 6))
            plt.plot(target.index,
                     self.scaler.inverse_transform(target[self.columns[sensor_idx]].values.reshape(-1, 1)),
                     color='blue',
                     label='raw data')
            plt.legend()
            plt.show()

            plt.figure(figsize=(12, 6))
            plt.plot(target.index[len(target.index) - len(predicted_sensor):],
                     predicted_sensor,
                     color='green',
                     label='predicted data')
            plt.legend()

            anomaly_df = pd.DataFrame(target[self.seq_len:])
            anomaly_df['target_mae'] = target_mae
            anomaly_df['threshold'] = self.threshold
            anomaly_df['anomaly'] = anomaly_df['target_mae'] > anomaly_df['threshold']
            anomaly_df[self.columns[sensor_idx]] = target[self.seq_len:][self.columns[sensor_idx]]

            anomalies = anomaly_df.loc[anomaly_df['anomaly'] == True]

            if not anomalies.empty:
                sns.scatterplot(x=anomalies.index,
                                y=self.scaler.inverse_transform(anomalies[self.columns[sensor_idx]].values.reshape(-1, 1)).flatten(),
                                color='r')
            plt.show()
