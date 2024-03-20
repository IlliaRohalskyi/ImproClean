"""
Data Transformation Module.

This module provides a class with a method for data transformation tasks
"""
from dataclasses import dataclass
from typing import List

import miceforest as mf
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from src.logger import logging
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

    def select_data(self, df, select_target=True) -> pd.DataFrame:
        """
        Selects columns from the DataFrame that start with the
        specified in the config file strings.

        Args:
            df: The DataFrame to be processed.

        Returns:
            A new DataFrame that contains only the columns that start with the specified strings.

        """
        logging.info("Selecting the data")
        column_startswith = self.transformation_config["features"]

        if "all" in column_startswith:
            start_names = [
                "Ziel",
                "Innoculum",
                "Waschen",
                "Ablagerung",
                "Prozess",
                "DoE",
                "timestamp",
            ]

            if not select_target:
                start_names.extend(["Red KBE", "Energie"])

            column_mapping = ~df.columns.str.startswith(tuple(start_names))

        else:
            if select_target:
                column_startswith.extend(["Red KBE", "Energie"])
            start_names = tuple(column_startswith)
            column_mapping = df.columns.str.startswith(start_names)

        return df.loc[:, column_mapping]

    def clean_data(self, df, validation_issues) -> pd.DataFrame:
        """
        Cleans the data by imputing missing values and removing duplicates.

        Args:
            df: The DataFrame to be cleaned.
            validation_issues: A list of validation issues detected by the data validation step.

        Returns:
            The cleaned DataFrame.
        """
        logging.info("Data cleaning started")

        if "duplicates" in validation_issues:
            logging.info("Removing duplicates")
            df.drop_duplicates(inplace=True)

        if "nan_imputable" in validation_issues:
            logging.info("Imputing NaN")
            df_array = df.to_numpy()
            kds = mf.ImputationKernel(
                df_array, save_all_iterations=True, random_state=42
            )
            kds.mice(10)
            imputed_array = kds.complete_data()
            df = pd.DataFrame(imputed_array, columns=df.columns)
        return df

    def create_train_test_split(self, transformed_data) -> TrainTestData:
        """
        Splits the data into training and testing sets.

        Args:
            transformed_data: The transformed DataFrame.

        Returns:
            A TrainTestData object containing the training and testing data,
            as well as the feature names.
        """
        logging.info("Creating train test splits")
        train_data, test_data = train_test_split(
            transformed_data,
            shuffle=True,
            test_size=0.2,
            random_state=42,
        )

        y_train = train_data[
            [
                col
                for col in train_data.columns
                if col.startswith("Red KBE") or col.startswith("Energie")
            ]
        ]
        x_train = train_data[
            [
                col
                for col in train_data.columns
                if not col.startswith("Red KBE") and not col.startswith("Energie")
            ]
        ]

        y_test = test_data[
            [
                col
                for col in test_data.columns
                if col.startswith("Red KBE") or col.startswith("Energie")
            ]
        ]
        x_test = test_data[
            [
                col
                for col in test_data.columns
                if not col.startswith("Red KBE") and not col.startswith("Energie")
            ]
        ]

        return TrainTestData(
            x_train=np.array(x_train),
            y_train=np.array(y_train),
            x_test=np.array(x_test),
            y_test=np.array(y_test),
            feature_names=x_train.columns,
        )
