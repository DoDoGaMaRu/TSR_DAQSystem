import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import asyncio
import seaborn as sns

from pandas import DataFrame
from .base_model import BaseModel
from sklearn.preprocessing import StandardScaler


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

    async def detect(self, target: DataFrame, plot_on: bool = False) -> int:
        loop = asyncio.get_event_loop()
        target_input = await self._data_to_input(self.scaler.fit_transform(target))
        target_predict = await loop.run_in_executor(None,
                                                    self.predict,
                                                    target_input, self.batch_size, "auto", None, None, 10, 4, False)
        target_mae = np.mean(np.abs(target_predict - target_input), axis=1)

        if plot_on:
            plt.plot(target_mae)
            plt.show()

        predicted_sensor = self.scaler.inverse_transform(target_predict[:, -1, 0].reshape(-1, 1))

        anomaly_df = pd.DataFrame(target[self.seq_len:])
        anomaly_df['target_mae'] = target_mae
        anomaly_df['threshold'] = self.threshold
        anomaly_df['anomaly'] = anomaly_df['target_mae'] > anomaly_df['threshold']
        anomaly_df['data'] = target[self.seq_len:]['data']
        anomalies = anomaly_df.loc[anomaly_df['anomaly'] == True]

        if plot_on:
            plt.figure(figsize=(12, 6))
            plt.plot(target.index,
                     self.scaler.inverse_transform(target['data'].values.reshape(-1, 1)),
                     color='blue',
                     label='raw data')
            plt.legend()

            plt.figure(figsize=(12, 6))
            plt.plot(target.index[len(target.index) - len(predicted_sensor):],
                     predicted_sensor,
                     color='green',
                     label='predicted data',
                     zorder=1)
            plt.legend()
            if not anomalies.empty:
                sns.scatterplot(x=anomalies.index,
                                y=self.scaler.inverse_transform(anomalies['data'].values.reshape(-1, 1)).flatten(),
                                color='r',
                                zorder=2)
            plt.show()
        return len(anomalies)
