from models.lstm_ae import LstmAE
from config import ModelConfig
import pandas as pd

model = LstmAE()
target = pd.read_csv('resources/data/cDAQ1Mod1_ai0/jun_20230604_cDAQ1Mod1_ai0.csv', names=['time', 'cDAQ1Mod1_ai0'])
target.drop(labels='time', axis=1, inplace=True)

# 학습시 아래 코드 사용. 컨픽 수정 필요
# model.train('resources/data')

# 모델 불러오기 시 아래 코드 사용
model.build((None, ModelConfig.SEQ_LEN, ModelConfig.INPUT_DIM))
model.load_weights('lstm_ae.h5')

model.summary()
# model.eval('resources/data')
model.detect(target)
