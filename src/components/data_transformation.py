"""
Data Transformation Module.

This module provides a class with a method for data transformation tasks
"""
from dataclasses import dataclass
from typing import List

import numpy as np
import pandas as pd

from src.utility import get_cfg


@dataclass
class TrainTestData:
    """
    Container for training and testing data along with feature names.
    """

    x_train: np.ndarray
    y_train: np.ndarray
    x_test: np.ndarray
    y_test: np.ndarray
    feature_names: List[str]


class DataTransformation:
    """
    Data transformation class.

    This class provides a method for data transformation tasks.

    Attributes:
        transformation_config (dict):
        The configuration settings for data transformation tasks
    """

    def __init__(self):
        """
        Initialize the DataTransformation instance.

        Attributes:
            self.transformation_config (dict): Configuration settings for data transformation tasks.
        """
        self.transformation_config = get_cfg("components/data_transformation.yaml")

    def select_data(self, df) -> pd.DataFrame:
        """
        Selects columns from the DataFrame that start with the
        specified in the config file strings.

        Args:
            df: The DataFrame to be processed.

        Returns:
            A new DataFrame that contains only the columns that start with the specified strings.

        """
        column_startswith = self.transformation_config["column_startswith"]

        if "all" in column_startswith:
            start_names = (
                "Ziel",
                "Innoculum",
                "Waschen",
                "Ablagerung",
                "Prozess",
                "DoE",
                "timestamp",
            )
            column_mapping = ~df.columns.str.startswith(start_names)

        else:
            start_names = tuple(column_startswith)
            column_mapping = df.columns.str.startswith(start_names)

        return df.loc[:, column_mapping]

    def clean_data(self, df, validation_issues) -> pd.DataFrame:
        """under development"""
        return df, validation_issues

    def create_train_test_split(self, transformed_data) -> TrainTestData:
        """under development"""
        return transformed_data


if __name__ == "__main__":
    from src.components.data_ingestion import DataIngestion

    data = DataIngestion().initiate_data_ingestion()
    print(DataTransformation().select_data(data))
