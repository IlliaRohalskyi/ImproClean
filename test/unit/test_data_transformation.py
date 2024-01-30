"""
Test Data Transformation.

This module contains test cases for the DataTransformation class
from the data_transformation module.
"""
from test.test_utility import create_synthetic_data

import numpy as np
import pandas as pd
import pytest

from src.components.data_transformation import DataTransformation
from src.utility import get_cfg


@pytest.fixture(name="data_transformation_object")
def fixture_transformation_object():
    """
    Fixture for DataTransformation Object.

    This fixture creates and returns an instance of the DataTransformation class.
    Changes the path of the config file to the test one

    Returns:
        DataTransformation: An instance of the DataTransformation class.
    """
    data_transformation_object = DataTransformation()
    data_transformation_object.transformation_config = get_cfg(
        "test/unit/test_data_transformation.yaml"
    )
    return data_transformation_object


@pytest.fixture(name="synthetic_data")
def fixture_synthetic_data():
    """
    Fixture for Synthetic Data

    This fixture creates and returns sample data

    Returns:
        pd.DataFrame: Synthetic data for test cases
    """
    return create_synthetic_data()


def test_data_selection(data_transformation_object, synthetic_data):
    """
    Test Data Selection Functionality.

    This test case verifies the functionality of the select_data method
    in the DataTransformation class.

    Args:
        data_transformation_object (DataTransformation): An instance of the DataTransformation class
        synthetic_data (pd.DataFrame): Synthetic data
    """
    selected_data = data_transformation_object.select_data(synthetic_data)

    # Check data types
    assert isinstance(
        selected_data, pd.DataFrame
    ), "Selected data should be a DataFrame"

    # Check if dataframes are not empty
    assert not selected_data.empty, "Dataframe should not be empty"

    # Check if dataframes of different length after selection
    assert len(synthetic_data.columns) > len(selected_data.columns)


def test_train_test_split(data_transformation_object, synthetic_data):
    """
    Test Data Train Test Split Functionality.

    This test case verifies the functionality of the create_train_test_split method
    in the DataTransformation class.

    Args:
        data_transformation_object (DataTransformation): An instance of the DataTransformation class
        synthetic_data (pd.DataFrame): Synthetic data
    """
    train_test_split = data_transformation_object.create_train_test_split(
        synthetic_data
    )

    assert (
        len(synthetic_data.columns) - len(train_test_split.feature_names) == 2
    ), "There should be two targets"

    assert not any(
        col.startswith("Red KBE") or col.startswith("Energie")
        for col in train_test_split.feature_names
    ), "Wrong target selection"


def test_clean_data(data_transformation_object, synthetic_data):
    """
    Test Data Cleaning Functionality.

    This test case verifies the functionality of the clean_data method
    in the DataTransformation class.

    Args:
        data_transformation_object (DataTransformation): An instance of the DataTransformation class
        synthetic_data (pd.DataFrame): Synthetic data
    """
    rand_col_idx = np.random.randint(0, len(synthetic_data.columns))

    nan_percent = 0.05
    mask = np.random.choice(
        [False, True], size=synthetic_data.shape[0], p=[1 - nan_percent, nan_percent]
    )
    synthetic_data.iloc[:, rand_col_idx][mask] = np.nan
    synthetic_data_duplicated = pd.concat(
        [synthetic_data, synthetic_data.sample(50)], ignore_index=True
    )
    clean_data = data_transformation_object.clean_data(
        synthetic_data, ["nan_imputable", "duplicates"]
    )

    # Assert if there are any duplicates
    assert (
        clean_data.duplicated().any() is False
    ), "clean_data should have no duplicates"

    # Assert if there are NaN values
    assert (
        clean_data.isnull().values.any() is False
    ), "clean_data should have no NaN values"

    # Assert if columns are different
    assert any(
        synthetic_data_duplicated.columns == clean_data.columns
    ), "clean_data columns should not be changed"
