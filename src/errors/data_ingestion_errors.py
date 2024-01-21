"""
This module contains all the errors for data_ingestion.py module
"""


class UnsupportedFileTypeError(Exception):
    """
    Error that is raised when an unsupported file type is encountered during data ingestion.

    Args:
        file_type (str): The file type that is not supported.
    """

    def __init__(self, file_dir):
        super().__init__(
            f"No supported files in the {file_dir} directory. "
            "Supported extensions are .xlsx, .xls, .csv"
        )


class PostgreSQLConnectionError(Exception):
    """
    Error that is raised when an error occurs while establishing a connection
    to the PostgreSQL database.
    """

    def __init__(self):
        super().__init__(
            "Connection error. Please verify your database credentials "
            "and check database availability."
        )


class ReadingError(Exception):
    """
    Error that is raised when an error occurs while reading data
    from the PostgreSQL database.
    """

    def __init__(self):
        super().__init__("Reading error. Failed to read the data from the database.")


class MultipleFilesError(Exception):
    """
    Error that is raised when the folder has multiple files, that could be read.
    The folder should have only one data file
    """

    def __init__(self):
        super().__init__("Multiple files error. Too many files to read.")
