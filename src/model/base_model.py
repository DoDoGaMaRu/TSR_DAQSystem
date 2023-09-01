import numpy as np

from keras.models import Model
from keras.layers import LSTM, RepeatVector, TimeDistributed, Dense
from model_config import ModelConfig


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


class BaseModel(Model):
    def __init__(self):
        super(BaseModel, self).__init__()
        self.encoder = Encoder(ModelConfig.SEQ_LEN, ModelConfig.LATENT_DIM)
        self.decoder = Decoder(ModelConfig.INPUT_DIM, ModelConfig.LATENT_DIM)

    def call(self, inputs, training=None, mask=None):
        z, z_rep = self.encoder(inputs)
        decoded = self.decoder(z_rep)

        return decoded

    async def _data_to_input(self, data: list) -> object:
        # LSTM의 입력 데이터로 변환하는 메소드
        # (입력 데이터 수, 시퀀스 길이, 사용할 컬럼 수)의 형태가 되어야 함
        data_list = []

        for i in range(len(data) - self.seq_len):
            data_list.append(data[i:(i + self.seq_len)])

        return np.array(data_list)
