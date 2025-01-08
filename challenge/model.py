from typing import List, Tuple, Union

import joblib
import numpy as np
import pandas as pd
from sklearn.utils import shuffle

class InputDataException(Exception):
    """Exception class for errors in input data for model"""


class DelayModel:
    MODEL_PATH = 'challenge/logistic_model.pkl'
    ENCODER_PATH = 'challenge/onehot_encoder.pkl'

    DELAY_THRESHOLD_MINUTES = 15
    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
    SCHEDULED_TIME = 'Fecha-I'
    REAL_TIME = 'Fecha-O'
    
    PRE_FEATURE_COLS = ['OPERA', 'TIPOVUELO', 'MES']
    FEATURE_COLS = [
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
        self._model = joblib.load(self.MODEL_PATH)
        self._encoder = joblib.load(self.ENCODER_PATH)

    def _check_required_columns(self, data: pd.DataFrame, target_column: str) -> None:
        required_columns = self.PRE_FEATURE_COLS.copy()

        if target_column:
            required_columns += [self.SCHEDULED_TIME, self.REAL_TIME]
        
        missing_columns = set(required_columns) - set(data.columns)
        
        if missing_columns:
            raise InputDataException(f"Missing required columns: {', '.join(missing_columns)}")


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
        try:
            # Check data validity
            self._check_required_columns(data, target_column)

            # Transform data with OneHotEncoder
            features = pd.DataFrame(
                self._encoder.transform(data[self.PRE_FEATURE_COLS]),
                columns=self._encoder.get_feature_names_out(self.PRE_FEATURE_COLS),
                index=data.index
            )

            # Keep 10 most important features
            features = features[self.FEATURE_COLS]

            if not target_column:

                return features
            else:
                # Calculate delay and then target
                real_time = pd.to_datetime(data[self.REAL_TIME], format=self.DATETIME_FORMAT)
                scheduled_time = pd.to_datetime(data[self.SCHEDULED_TIME], format=self.DATETIME_FORMAT)
                time_diff_minutes = ((real_time - scheduled_time).dt.total_seconds())/60
                target = np.where(time_diff_minutes > self.DELAY_THRESHOLD_MINUTES, 1, 0)
                target = pd.DataFrame(data={target_column: target}, index=features.index)

                return features, target
        except ValueError as e:
            if 'Found unknown categories' in str(e):  # Raised by One Hot Encoder
                unknown_categories, column_index = str(e).split("Found unknown categories")[1].split("in column ")
                unknown_categories = unknown_categories.strip().strip("[]").replace("'", "")
                column_name = self.PRE_FEATURE_COLS[int(column_index.split(' ')[0])]
                
                # Raise error with improved message
                raise InputDataException(f"Unknown categories '{unknown_categories}' found in column '{column_name}'")
            else:
                raise
           

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