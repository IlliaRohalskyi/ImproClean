"""
Module for utility functions used in testing.

This module contains functions for creating synthetic data and uploading data
to a PostgreSQL database.
"""

import os

import numpy as np
import pandas as pd
from sqlalchemy import create_engine

from src.components.data_ingestion import DataIngestion
from src.utility import get_cfg, get_root


def create_synthetic_data():
    """
    Creates synthetic data based on the configuration file.

    Returns:
        pd.DataFrame: A synthetic DataFrame with random data.
    """
    config = get_cfg("test/test_utility.yaml")
    row_count = config["row_count"]

    df = DataIngestion().initiate_data_ingestion()

    synthetic_df = pd.DataFrame(np.random.normal(size=(row_count, len(df.columns))))

    synthetic_df.columns = df.columns

    return synthetic_df


def upload_data(path: str, table_name: str):
    """
    Uploads the data from a CSV file to the PostgreSQL database.

    Args:
        path (str): The path to the CSV file to upload.
        table_name (str): The name of the table in the PostgreSQL database to upload the data to.
    """
    hostname = os.environ.get("DB_HOSTNAME")
    database_name = os.environ.get("DB_NAME")
    username = os.environ.get("DB_USERNAME")
    password = os.environ.get("DB_PASSWORD")

    absolute_path = os.path.join(get_root(), path)

    engine = create_engine(
        f"postgresql://{username}:{password}@{hostname}/{database_name}"
    )

    data = pd.read_excel(absolute_path)

    data.to_sql(table_name, engine, if_exists="replace", index=False)
