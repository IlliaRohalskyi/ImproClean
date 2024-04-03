"""
This module contains all the errors for data_validation.py module
"""


class ColumnsDiffError(Exception):
    """
    Error that is raised when columns are different between DataFrames and provides details about the difference.
    """

    def __init__(self, df1, df2):
        """
        Args:
            df1: The first DataFrame to compare.
            df2: The second DataFrame to compare.
        """
        self.df1_cols = df1.columns.tolist()
        self.df2_cols = df2.columns.tolist()
        self.diff_cols = set(self.df1_cols) ^ set(self.df2_cols)
        message = "Columns are different between DataFrames:\n"
        if self.diff_cols:
            message += f"Missing columns in DataFrame1: {', '.join(self.diff_cols - set(self.df2_cols))}\n"
            message += f"Missing columns in DataFrame2: {', '.join(self.diff_cols - set(self.df1_cols))}"
        else:
            if self.df1_cols != self.df2_cols:
                message += "Column order is different between DataFrames."
        super().__init__(message)


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
