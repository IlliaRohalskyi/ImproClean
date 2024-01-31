"""
Test Data Integration.

This module contains test cases for integrating data-related modules.
"""
import os
from test.test_utility import create_cat_col, upload_data

import pandas as pd
import pytest

from src.components.data_ingestion import DataIngestion
from src.components.data_transformation import DataTransformation
from src.components.data_validation import DataValidation
from src.utility import get_cfg


@pytest.fixture(name="data_ingestion_object")
def fixture_data_ingestion_object():
    """
    Fixture for DataIngestion Object.

    This fixture creates and returns an instance of the DataIngestion class.
    Changes the path of the data to the test file

    Returns:
        DataIngestion: An instance of the DataIngestion class.
    """
    data_ingestion_object = DataIngestion()
    data_ingestion_object.ingestion_config = get_cfg(
        "test/unit/test_data_ingestion.yaml"
    )
    return data_ingestion_object


@pytest.fixture(name="data_validation_object")
def fixture_validation_object():
    """
    Fixture for DataValidation Object.

    This fixture creates and returns an instance of the DataValidation class.
    Changes the path of the config file to the test one

    Returns:
        DataValidation: An instance of the DataValidation class.
    """
    data_transformation_object = DataValidation()
    data_transformation_object.validation_config = get_cfg(
        "test/unit/test_data_validation.yaml"
    )
    return data_transformation_object


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


@pytest.mark.integration()
def test_training_data_integration(
    data_ingestion_object, data_validation_object, data_transformation_object
):
    """
    Test the training data integration process.

    This test case verifies the functionality of the data ingestion,
    data selection, and data validation stages for training data.
    """
    df = data_ingestion_object.initiate_data_ingestion()
    selected_df = data_transformation_object.select_data(df)
    val_issues = data_validation_object.check_training_data(selected_df)
    clean_data = data_transformation_object.clean_data(selected_df, val_issues)


@pytest.mark.integration()
def test_pred_data_integration(
    data_ingestion_object, data_validation_object, data_transformation_object
):
    """
    Test the prediction data integration process.

    This test case verifies the functionality of the data ingestion,
    data selection, and data validation stages for prediction data.
    """
    data_path = os.path.join(
        data_ingestion_object.ingestion_config["training_data_folder_path"],
        "synthetic_unformatted.xlsx",
    )

    upload_data(data_path, "synthetic_unformatted")

    pred_df = data_ingestion_object.get_sql_table("synthetic_unformatted")
    train_df = data_ingestion_object.initiate_data_ingestion()

    pred_df_selected = data_transformation_object.select_data(pred_df)
    train_df_selected = data_transformation_object.select_data(train_df)

    train_df_cat = create_cat_col(train_df_selected, [0.65, 0.3, 0.05])
    pred_df_cat = create_cat_col(pred_df_selected, [0.65, 0.3, 0.05])

    val_issues = data_validation_object.check_prediction_data(pred_df_cat, train_df_cat)
    clean_data = data_transformation_object.clean_data(pred_df_cat, val_issues)
