"""
Module for integration testing of the prediction pipeline.

This module contains an integration test function that uploads synthetic data,
runs the prediction pipeline, and then deletes the specified table from the database.
"""

import os
from test.test_utility import upload_data

import psycopg2

from src.pipelines.prediction_pipeline import prediction_pipeline
from src.utility import get_cfg, get_root


def test_pred_integration():
    """
    Integration test for the prediction pipeline.

    This test uploads synthetic data, runs the prediction pipeline, and then deletes
    the specified table from the database.

    Returns:
        None
    """
    test_data_path = os.path.join(
        get_root(),
        "test",
        "synthetic_data",
        "unformatted",
        "synthetic_unformatted.xlsx",
    )
    cfg = get_cfg("test/integration/test_prediction_pipeline.yaml")
    upload_data(test_data_path, cfg["prediction_table"])
    prediction_pipeline(cfg)

    hostname = os.environ.get("DB_HOSTNAME")
    database_name = os.environ.get("DB_NAME")
    username = os.environ.get("DB_USERNAME")
    password = os.environ.get("DB_PASSWORD")

    connection = psycopg2.connect(
        host=hostname, database=database_name, user=username, password=password
    )

    cursor = connection.cursor()

    delete_query = f"DELETE FROM {cfg['write_table']}"

    cursor.execute(delete_query)
    connection.commit()

    cursor.close()
    connection.close()
