"""
Training Error Module.

Contains all errors for training module
"""
import sys


def error_message_details(error, error_detail: sys) -> str:
    """
    Generate an error message with details.

    This function constructs an error message with information about the error,
    including the script name, line number, and error message.

    Args:
        error (Exception): The exception object containing the error message.
        error_detail (sys): The sys module detail of the error.

    Returns:
        str: The formatted error message.
    """
    _, _, exc_tb = error_detail.exc_info()
    filename = exc_tb.tb_frame.f_code.co_filename
    error_message = (
        f"Error occurred in python script name [{filename}] "
        f"line number [{exc_tb.tb_lineno}] "
        f"error message [{error}]"
    )

    return error_message


class PlotError(Exception):
    """
    Plot Error Class.

    Raised when error in the plot creation occurred.

    Args:
        error_message (str): The error message.
        error_detail (sys): The sys module detail of the error.

    Attributes:
        error_message (str): The formatted error message.
    """

    def __init__(self, error_message, error_detail: sys):
        """
        Initialize the instance.

        Args:
            error_message (Exception): The exception object containing the error message.
            error_detail (sys): The sys module detail of the error.
        """
        super().__init__(error_message)
        self.error_message = error_message_details(
            error_message, error_detail=error_detail
        )

    def __str__(self):
        """
        Return the error message.

        Returns:
            str: The formatted error message.
        """
        return self.error_message


class EnsembleMetricsError(Exception):
    """
    Ensemble Metrics Error Class.

    Raised when error occurred when logging ensemble metrics.

    Args:
        error_message (str): The error message.
        error_detail (sys): The sys module detail of the error.

    Attributes:
        error_message (str): The formatted error message.
    """

    def __init__(self, error_message, error_detail: sys):
        """
        Initialize the instance.

        Args:
            error_message (Exception): The exception object containing the error message.
            error_detail (sys): The sys module detail of the error.
        """
        super().__init__(error_message)
        self.error_message = error_message_details(
            error_message, error_detail=error_detail
        )

    def __str__(self):
        """
        Return the error message.

        Returns:
            str: The formatted error message.
        """
        return self.error_message


class TrainLogError(Exception):
    """
    Train Log Error Class.

    Raised when error occurred when training the model and logging results.

    Args:
        error_message (str): The error message.
        error_detail (sys): The sys module detail of the error.

    Attributes:
        error_message (str): The formatted error message.
    """

    def __init__(self, error_message, error_detail: sys):
        """
        Initialize the instance.

        Args:
            error_message (Exception): The exception object containing the error message.
            error_detail (sys): The sys module detail of the error.
        """
        super().__init__(error_message)
        self.error_message = error_message_details(
            error_message, error_detail=error_detail
        )

    def __str__(self):
        """
        Return the error message.

        Returns:
            str: The formatted error message.
        """
        return self.error_message


class ReportError(Exception):
    """
    Report Error Class.

    Raised when error occurred when building a report.

    Args:
        error_message (str): The error message.
        error_detail (sys): The sys module detail of the error.

    Attributes:
        error_message (str): The formatted error message.
    """

    def __init__(self, error_message, error_detail: sys):
        """
        Initialize the instance.

        Args:
            error_message (Exception): The exception object containing the error message.
            error_detail (sys): The sys module detail of the error.
        """
        super().__init__(error_message)
        self.error_message = error_message_details(
            error_message, error_detail=error_detail
        )

    def __str__(self):
        """
        Return the error message.

        Returns:
            str: The formatted error message.
        """
        return self.error_message
