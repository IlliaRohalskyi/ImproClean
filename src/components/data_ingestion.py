"""
Data Ingestion Module.

This module provides a class with a method for data ingestion tasks
"""
import os

import pandas as pd
import psycopg2

from src.logger import logging
from src.utility import get_cfg, get_root


class DataIngestion:
    """
    Data ingestion class.

    This class provides a method for data ingestion tasks.

    Attributes:
        ingestion_config (DataIngestionConfig): The configuration settings for data ingestion tasks.
    """

    def __init__(self):
        """
        Initialize the DataIngestion instance.

        Args:
            ingestion_config (dict): Configuration settings for data ingestion tasks.
        """
        self.ingestion_config = get_cfg(
            os.path.join(get_root(), ".cfg/components/data_ingestion.yaml")
        )

    def initiate_data_ingestion(self) -> pd.DataFrame:
        """
        Initiate the data ingestion process.

        This method triggers the ingestion of data as specified
        in the configuration. It returns the pandas dataframe

        Returns:
            pandas.DataFrame: A DataFrame containing the ingested training data
        """

        logging.info("Initiating data ingestion")

        file_type = self.ingestion_config["training_data_path"].split(".")[-1]

        file_path = os.path.join(
            get_root(), self.ingestion_config["training_data_path"]
        )

        if file_type in ["xls", "xlsx"]:
            data = pd.read_excel(file_path)
        elif file_type == "csv":
            data = pd.read_csv(file_path)
        else:
            logging.error("Unsupported data type error")
            raise UnsupportedFileTypeError(file_type)

        logging.info("Data ingestion completed successfully")
        return data

    def get_sql_table(self, table_name) -> pd.DataFrame:
        """
        Initiate the data ingestion process from a Postgres database.

        This method triggers the ingestion of data from the database

        Returns:
            pandas.DataFrame: A DataFrame containing the ingested data.
        """
        hostname = os.environ.get("DB_HOSTNAME")
        database_name = os.environ.get("DB_NAME")
        username = os.environ.get("DB_USERNAME")
        password = os.environ.get("DB_PASSWORD")

        try:
            connection = psycopg2.connect(
                host=hostname, database=database_name, user=username, password=password
            )

        except ConnectionException as e:
            logging.error("Error connecting to PostgreSQL:", e)

        query = f"SELECT * FROM {table_name};"

        try:
            data = pd.read_sql_query(query, connection)
        except ReadingError as e:
            logging.error("Error executing SQL query:", e)

        if connection:
            connection.close()
        return data


class UnsupportedFileTypeError(Exception):
    """
    Exception raised when an unsupported file type is encountered during data ingestion.

    Args:
        file_type (str): The file type that is not supported.
    """

    def __init__(self, file_type):
        super().__init__(
            f"The file type '{file_type}' is not supported. Supported file types are:"
            f" .xlsx, .xls, and .csv."
        )


class ConnectionException(Exception):
    """
    Exception raised when an error occurs while establishing a connection
    to the PostgreSQL database.
    """

    def __init__(self):
        super().__init__(
            "Connection error. Please verify your database credentials "
            "and check database availability."
        )


class ReadingError(Exception):
    """
    Exception raised when an error occurs while reading data
    from the PostgreSQL database.
    """

    def __init__(self):
        super().__init__("Reading error. Failed to read the data from the database.")
