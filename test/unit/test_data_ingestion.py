"""
Test Data Ingestion.

This module contains test cases for the DataIngestion class
 from the data_ingestion module.
"""
import os
from test.test_utility import upload_data

import pandas as pd
import pytest

from src.components.data_ingestion import DataIngestion
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


def test_data_ingestion(data_ingestion_object):
    """
    Test Data Ingestion Functionality.

    This test case verifies the functionality of the initiate_data_ingestion method
    in the DataIngestion class.

    Args:
        data_ingestion_object (DataIngestion): An instance of the DataIngestion class.
    """
    df = data_ingestion_object.initiate_data_ingestion()

    # Check data types
    assert isinstance(df, pd.DataFrame), "Ingested data should be a DataFrame"

    # Check if dataframes are not empty
    assert not df.empty, "Dataframe should not be empty"


def test_sql_ingestion(data_ingestion_object):
    """
    Test the SQL data ingestion method.

    This function tests the data ingestion from a SQL table and
    checks if the retrieved data is a DataFrame

    Args:
        data_ingestion_object (DataIngestion): An instance of the DataIngestion class..
    """
    data_path = os.path.join(
        data_ingestion_object.ingestion_config["training_data_folder_path"],
        "synthetic_unformatted.xlsx",
    )

    upload_data(data_path, "synthetic_unformatted")
    data = data_ingestion_object.get_sql_table("synthetic_unformatted")
    assert isinstance(data, pd.DataFrame), "SQL data should be a DataFrame"
