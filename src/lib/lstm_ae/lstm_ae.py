
import pandas as pd
import numpy as np

from pandas import DataFrame
from sklearn.preprocessing import StandardScaler

from .base_model import BaseModel


class LstmAE(BaseModel):
    def __init__(self,
                 seq_len: int,
                 input_dim: int,
                 latent_dim: int,
                 batch_size: int,
                 threshold: float):
        super(LstmAE, self).__init__(seq_len=seq_len,
                                     input_dim=input_dim,
                                     latent_dim=latent_dim)
        self.batch_size = batch_size
        self.threshold = threshold

        self.scaler = StandardScaler()

    def detect(self, target: DataFrame) -> int:
        target_input = self._data_to_input(self.scaler.fit_transform(target))
        target_predict = self.__call__(target_input)
        target_mae = np.mean(np.abs(target_predict - target_input), axis=1)

        anomaly_df = pd.DataFrame(target[self.seq_len:])
        anomaly_df['target_mae'] = target_mae
        anomaly_df['threshold'] = self.threshold
        anomaly_df['anomaly'] = anomaly_df['target_mae'] > anomaly_df['threshold']
        anomaly_df['data'] = target[self.seq_len:]['data']
        anomalies = anomaly_df.loc[anomaly_df['anomaly'] == True]

        return len(anomalies)
