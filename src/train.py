from daq_system.machine.fault_detector.lstm_ae import LstmAE
from config import ModelConfig
import pandas as pd
import os
import matplotlib.pyplot as plt

model = LstmAE()

# 학습시 아래 코드 사용. 컨픽 수정 필요
# model.train('resources/data')

# 모델 불러오기 시 아래 코드 사용
model.build((None, ModelConfig.SEQ_LEN, ModelConfig.INPUT_DIM))
model.load_weights('resources/model/ShotBlast.h5')

model.summary()
# model.eval('resources/data')
# target = pd.read_csv('resources/data/cDAQ1Mod1_ai0/jun_20230612_cDAQ1Mod1_ai0.csv', names=['time', 'cDAQ1Mod1_ai0'])
# target.drop(columns=['time'], axis=1, inplace=True)
# print(model.detect(target, plot_on=True))

for (root, directories, files) in os.walk('resources/data/cDAQ1Mod1_ai0'):
    for file in files:
        if '.csv' in file:
            target = pd.read_csv(f'resources/data/cDAQ1Mod1_ai0/{file}', names=['time', 'cDAQ1Mod1_ai0'])
            target.drop(columns=['time'], axis=1, inplace=True)
            # 데이터 탐지
            print(model.detect(target, plot_on=True))

            # 데이터 plot
            # plt.plot(target,
            #          label=f'{file}')
            # plt.legend()
            # plt.show()
