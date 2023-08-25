from models.lstm_ae import LstmAE
from config import ModelConfig

model = LstmAE()

# 학습시 아래 코드 사용. 컨픽 수정 필요
#model.train('resources/data')

# # 모델 불러오기 시 아래 코드 사용
model.build((None, ModelConfig.SEQ_LEN, ModelConfig.INPUT_DIM))
model.load_weights('lstm_ae.h5')
#
model.summary()
model.validate('resources/data')
