"""
Test Data Transformation.

This module contains test cases for the DataTransformation class
from the data_transformation module.
"""
from test.test_utility import (
    create_duplicated_data,
    create_nan_data,
    create_synthetic_data,
)

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


def test_data_selection(data_transformation_object):
    """
    Test Data Selection Functionality.

    This test case verifies the functionality of the select_data method
    in the DataTransformation class.

    Args:
        data_transformation_object (DataTransformation): An instance of the DataTransformation class
    """
    synthetic_data = create_synthetic_data()
    selected_data = data_transformation_object.select_data(synthetic_data)

    # Check data types
    assert isinstance(
        selected_data, pd.DataFrame
    ), "Selected data should be a DataFrame"

    # Check if dataframes are not empty
    assert not selected_data.empty, "Dataframe should not be empty"

    # Check if dataframes of different length after selection
    assert len(synthetic_data.columns) > len(selected_data.columns)


def test_train_test_split(data_transformation_object):
    """
    Test Data Train Test Split Functionality.

    This test case verifies the functionality of the create_train_test_split method
    in the DataTransformation class.

    Args:
        data_transformation_object (DataTransformation): An instance of the DataTransformation class
    """
    synthetic_data = create_synthetic_data()
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


def test_clean_data(data_transformation_object):
    """
    Test Data Cleaning Functionality.

    This test case verifies the functionality of the clean_data method
    in the DataTransformation class.

    Args:
        data_transformation_object (DataTransformation): An instance of the DataTransformation class
    """
    nan_data = create_nan_data()
    synthetic_data = create_duplicated_data(nan_data)

    clean_data = data_transformation_object.clean_data(
        synthetic_data, ["nan_imputable", "duplicates"]
    )

    # Assert if there are any duplicates
    assert not clean_data.duplicated().any(), "clean_data should have no duplicates"

    # Assert if there are NaN values
    assert not clean_data.isnull().values.any(), "clean_data should have no NaN values"

    # Assert if columns are different
    assert any(
        synthetic_data.columns == clean_data.columns
    ), "clean_data columns should not be changed"
