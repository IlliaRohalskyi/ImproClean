"""
This module contains all the errors for data_validation.py module
"""


class ColumnsDiffError(Exception):
    """
    Error that is raised when columns are different between dataframes
    """

    def __init__(self):
        super().__init__("Columns are different between dataframes")


class DtypeDiffError(Exception):
    """
    Error that is raised when dtypes are different between dataframes
    """

    def __init__(self):
        super().__init__("Dtypes are different between dataframes")


class NanError(Exception):
    """
    Error that is raised when data contains too much nan and cannot be imputed
    """

    def __init__(self):
        super().__init__("Too many NaN values")
