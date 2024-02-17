"""
Data Ingestion Module.

This module provides a class with a method for data ingestion tasks
"""
import os

import pandas as pd
import psycopg2

from src.errors.data_ingestion_errors import (
    MultipleFilesError,
    PostgreSQLConnectionError,
    ReadingError,
    UnsupportedFileTypeError,
)
from src.logger import logging
from src.utility import get_cfg, get_root


class DataIngestion:
    """
    Data ingestion class.

    This class provides a method for data ingestion tasks.

    Attributes:
        ingestion_config (dict): The configuration settings for data ingestion tasks.
    """

    def __init__(self):
        """
        Initialize the DataIngestion instance.

        Attributes:
            self.ingestion_config (dict): Configuration settings for data ingestion tasks.
        """
        self.ingestion_config = get_cfg("components/data_ingestion.yaml")

    def _get_supported_file(self) -> str:
        """
        Retrieve the supported training data file from the specified directory.

        This method checks the training data folder for files with supported extensions
        (xls, xlsx, csv) and returns the matching file.
        If no supported files are found, an `UnsupportedFileTypeError` is raised.
        If more than one supported file is found, a `MultipleFilesError` is raised.

        Returns:
            str: Path to the supported training data file
        """
        dir_path = os.path.join(
            get_root(), self.ingestion_config["training_data_folder_path"]
        )

        file_list = os.listdir(dir_path)

        supported_file_types = ["xls", "xlsx", "csv"]

        supported_files = []

        for file_name in file_list:
            file_extension = file_name.split(".")[-1]
            if file_extension in supported_file_types:
                supported_files.append(os.path.join(dir_path, file_name))

        if not supported_files:
            logging.error("No supported files found in the training data folder")
            raise UnsupportedFileTypeError(dir_path)

        if len(supported_files) > 1:
            logging.error(
                "Only one file of supported format (xlsx, xls, csv) "
                "should exist in the training data folder"
            )
            raise MultipleFilesError

        return supported_files[0]

    def initiate_data_ingestion(self) -> pd.DataFrame:
        """
        Initiate the data ingestion process.

        This method triggers the ingestion of data.
        It returns the pandas dataframe

        Returns:
            pandas.DataFrame: A DataFrame containing the ingested training data
        """

        logging.info("Initiating data ingestion")

        supported_file = self._get_supported_file()

        if supported_file.endswith("csv"):
            data = pd.read_csv(supported_file)
        else:
            data = pd.read_excel(supported_file)

        logging.info("Data ingestion completed successfully")
        return data

    def get_sql_table(self, table_name) -> pd.DataFrame:
        """
        Initiate the data ingestion process from a Postgres database.

        This method triggers the ingestion of data from the database

        Args:
            table_name (str): The name of the table

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

        except PostgreSQLConnectionError as e:
            logging.error("Error connecting to PostgreSQL:", e)
            raise e
        query = f"SELECT * FROM {table_name};"

        try:
            data = pd.read_sql_query(query, connection)
        except ReadingError as e:
            logging.error("Error executing SQL query:", e)

        if connection:
            connection.close()
        return data
