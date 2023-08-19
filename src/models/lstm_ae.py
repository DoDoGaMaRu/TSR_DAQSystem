import os
import pandas as pd
import numpy as np

from keras.optimizers import Adam
from keras.models import Model
from keras.layers import LSTM, RepeatVector, TimeDistributed, Dense
from sklearn.model_selection import train_test_split
from config import ModelConfig, SensorConfig


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
    def __init__(self, input_dim):
        super(LstmAE, self).__init__()

        self.seq_length = ModelConfig.SEQ_LEN
        self.latent_dim = ModelConfig.LATENT_DIM
        self.test_size = ModelConfig.TEST_SIZE

        self.encoder = Encoder(self.seq_length, self.latent_dim)
        self.decoder = Decoder(input_dim, self.latent_dim)

    def call(self, inputs, training=None, mask=None):
        z, z_rep = self.encoder(inputs)
        decoded = self.decoder(z_rep)

        return decoded

    def _get_data(self, data_path: str) -> tuple:
        columns = []
        for device_config in SensorConfig.DEVICES:
            for channel_name in device_config.CHANNEL_NAMES:
                columns.append(channel_name)

        df = pd.DataFrame()
        for column in columns:
            for (root, directories, files) in os.walk(f'{data_path}/{column}'):
                for file in files:
                    if '.csv' in file:
                        file_path = os.path.join(root, file)
                        cur_df = pd.read_csv(file_path, names=['time', column])
                        df[column] = cur_df[column]

        train, test = train_test_split(df, test_size=self.test_size, shuffle=False)
        return train, test

    def _data_to_input(self, data: tuple) -> tuple:
        # LSTM의 입력 데이터로 변환하는 메소드
        # (입력 데이터 수, 시퀀스 길이, 사용할 컬럼 수)의 형태가 되어야 함
        train_input = []
        test_input = []
        train, test = data

        for i in range(len(train) - self.seq_len):
            train_input.append(train.iloc[i:(i + self.seq_len)].values)
        for i in range(len(test) - self.seq_len):
            test_input.append(test.iloc[i:(i + self.seq_len)].values)

        return np.array(train_input), np.array(test_input)

    def train(self):
        pass
        # train, test, scaler, _ = self._get_data('resources/data/jun_20230517_cDAQ1Mod1_ai0.csv')
        # # get train and test data
        # trainX = to_sequences(train[['Close']], seq_len)
        # print(trainX[0:5, 0, 0], train.head(5))
        #
        # input_dim = trainX.shape[2]
        #
        # # specify learning rate
        # learning_rate = 0.001
        # # create an Adam optimizer with the specified learning rate
        # optimizer = Adam(learning_rate=learning_rate)
        #
        # # create lstm_ae agent
        # lstm_ae = LstmAE(seq_len, input_dim, latent_dim)
        # lstm_ae.compile(optimizer=optimizer, loss='mse')
        #
        # # train
        # history = lstm_ae.fit(trainX, trainX, epochs=100, batch_size=32, validation_split=0.1, verbose=2)
        #
        # # save weights
        # lstm_ae.save_weights("./save_weights/lstm_ae.h5")
        #
        # # plotting
        # plt.plot(history.history['loss'], label='Training loss')
        # plt.plot(history.history['val_loss'], label='Validation loss')
        # plt.legend()
        # plt.show()
