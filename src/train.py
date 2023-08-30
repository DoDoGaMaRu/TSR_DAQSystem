from daq_system.machine.fault_detector.lstm_ae import LstmAE
import pandas as pd
from pandas import DataFrame
from config import ModelConfig

model = LstmAE()
target = pd.read_csv('resources/data/cDAQ1Mod1_ai0/jun_20230604_cDAQ1Mod1_ai0.csv', names=['time', 'cDAQ1Mod1_ai0'])
target.drop(labels='time', axis=1, inplace=True)
target = target[:150]
print(target)
temp = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
temp2 = DataFrame(temp, columns=['hi'])
print(temp2)

# 학습시 아래 코드 사용. 컨픽 수정 필요
# model.train('resources/data')

# 모델 불러오기 시 아래 코드 사용
# model.build((None, ModelConfig.SEQ_LEN, ModelConfig.INPUT_DIM))
# model.load_weights('lstm_ae.h5')
#
# model.summary()
# # model.eval('resources/data')
# print(model.detect(target, plot_on=True))
