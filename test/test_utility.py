"""
Module for utility functions used in testing.

This module contains functions for creating synthetic data and uploading data
to a PostgreSQL database.
"""

import os

import numpy as np
import pandas as pd
from sqlalchemy import create_engine

from src.utility import get_cfg, get_root


def create_synthetic_data() -> pd.DataFrame:
    """
    Creates synthetic data while maintaining original data types.

    Returns:
        pd.DataFrame: A synthetic DataFrame with random data.
    """
    config = get_cfg("test/test_utility.yaml")
    row_count = config["row_count"]

    path = os.path.join(
        get_root(), "test/synthetic_data/unformatted/synthetic_unformatted.xlsx"
    )
    df = pd.read_excel(path)

    synthetic_df = pd.DataFrame()
    for column in df.columns:
        if df[column].dtype == "float64":
            synthetic_df[column] = np.random.normal(size=row_count)
        elif df[column].dtype == "int64":
            synthetic_df[column] = np.random.randint(0, 100, size=row_count)
        else:
            synthetic_df[column] = np.random.choice(df[column], size=row_count)

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


def create_nan_data(nan_percent=0.05):
    """
    Creates synthetic data with NaN values.

    Args:
        nan_percent (float): Percentage of nan values

    Returns:
        pd.DataFrame: A synthetic DataFrame with NaN values.
    """
    synthetic_data = create_synthetic_data()
    rand_col_idx = np.random.randint(0, len(synthetic_data.columns))
    mask = np.random.choice(
        [False, True], size=synthetic_data.shape[0], p=[1 - nan_percent, nan_percent]
    )
    synthetic_data.iloc[:, rand_col_idx][mask] = np.nan
    return synthetic_data


def create_duplicated_data(data, fraction=0.05) -> pd.DataFrame:
    """
    Creates synthetic duplicated data.

    Args:
        data (pd.DataFrame): The data to which duplicates will be added
        fraction (float): Fraction of added duplicates

    Returns:
        pd.DataFrame: A synthetic DataFrame with duplicated values.
    """
    num_duplicates = int(len(data) * fraction)
    duplicated_indices = np.random.choice(data.index, size=num_duplicates, replace=True)
    duplicated_data = data.loc[duplicated_indices]
    result_data = pd.concat([data, duplicated_data], ignore_index=True)
    return result_data


def create_cat_col(data, p, colname="test_cat_col") -> pd.DataFrame:
    """
    Creates a column with a synthetic categorical data.

    Args:
        data (pd.DataFrame): Dataframe to which to add synthetic categorical column
        p (List[float]: List containing 3 p-values corresponding to each category
        colname (str): name of a column with categorical data

    Returns:
        pd.DataFrame: A synthetic Dataframe with a categorical column
    """
    categories = [0, 1, 2]
    data[colname] = np.random.choice(categories, size=len(data), p=p)
    return data
