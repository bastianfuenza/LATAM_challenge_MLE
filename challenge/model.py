from typing import List, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.utils import shuffle


class DelayModel:
    DELAY_THRESHOLD_MINUTES = 15
    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
    SCHEDULED_TIME = 'Fecha-I'
    REAL_TIME = 'Fecha-O'
    
    PREFEATURES_COLS = ['OPERA', 'TIPOVUELO', 'MES']
    FEATURES_COLS = [
        "OPERA_Latin American Wings", 
        "MES_7",
        "MES_10",
        "OPERA_Grupo LATAM",
        "MES_12",
        "TIPOVUELO_I",
        "MES_4",
        "MES_11",
        "OPERA_Sky Airline",
        "OPERA_Copa Air"
    ]




    def __init__(
        self
    ):
        self._model = LogisticRegression(class_weight='balanced')

    def preprocess(
        self,
        data: pd.DataFrame,
        target_column: str = None
    ) -> Union[Tuple[pd.DataFrame, pd.DataFrame], pd.DataFrame]:
        """
        Prepare raw data for training or predict.

        Args:
            data (pd.DataFrame): raw data.
            target_column (str, optional): if set, the target is returned.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: features and target.
            or
            pd.DataFrame: features.
        """
        features = pd.concat(
            [pd.get_dummies(data[col], prefix=col) for col in self.PREFEATURES_COLS], 
            axis = 1
        )

        features = features[self.FEATURES_COLS]

        if not target_column:

            return features
        else:
            # Calculate target from delay
            real_time = pd.to_datetime(data[self.REAL_TIME], format=self.DATETIME_FORMAT)
            scheduled_time = pd.to_datetime(data[self.SCHEDULED_TIME], format=self.DATETIME_FORMAT)
            time_diff_minutes = ((real_time - scheduled_time).dt.total_seconds())/60
            target = np.where(time_diff_minutes > self.DELAY_THRESHOLD_MINUTES, 1, 0)
            target = pd.DataFrame(data={target_column: target}, index=features.index)

            return features, target
           

    def fit(
        self,
        features: pd.DataFrame,
        target: pd.DataFrame
    ) -> None:
        """
        Fit model with preprocessed data.

        Args:
            features (pd.DataFrame): preprocessed data.
            target (pd.DataFrame): target.
        """
        x_train, y_train = shuffle(features, target)
        self._model.fit(x_train, y_train)

        return

    def predict(
        self,
        features: pd.DataFrame
    ) -> List[int]:
        """
        Predict delays for new flights.

        Args:
            features (pd.DataFrame): preprocessed data.
        
        Returns:
            (List[int]): predicted targets.
        """

        y_pred = self._model.predict(features)
        y_pred = y_pred.astype(int).tolist()

        return y_pred