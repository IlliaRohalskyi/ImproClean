"""
Module for defining common Prefect tasks used in machine learning pipelines.

Includes tasks for data ingestion, transformation, validation,
train-test split, and model training or retraining.

Tasks are designed to be reusable across different pipeline configurations.
"""

from prefect import task

from src.components.data_ingestion import DataIngestion
from src.components.data_transformation import DataTransformation
from src.components.data_validation import DataValidation
from src.components.model_trainer import ModelTrainer


@task
def get_data():
    """
    Task to initiate data ingestion using the DataIngestion component.

    Returns:
        The raw data obtained from the data ingestion process.
    """
    return DataIngestion().initiate_data_ingestion()


@task
def select_data(result):
    """
    Task to select relevant data using the DataTransformation component.

    Args:
        result: The raw data obtained from the data ingestion process.

    Returns:
        The selected subset of data.
    """
    return DataTransformation().select_data(result)


@task
def validate_data(result):
    """
    Task to perform data validation using the DataValidation component.

    Args:
        result: The selected subset of data.

    Returns:
        The cleaned data after validation checks.
    """
    validation_checks = DataValidation().check_training_data(result)
    if validation_checks:
        return DataTransformation().clean_data(result, validation_checks)
    return result


@task
def train_test_split(result):
    """
    Task to create a train-test split using the DataTransformation component.

    Args:
        result: The cleaned data after validation checks.

    Returns:
        The train-test split data.
    """
    return DataTransformation().create_train_test_split(result)


@task
def train_model(result):
    """
    Task to initiate model training using the ModelTrainer component.

    Args:
        result: The train-test split data.

    Returns:
        None
    """
    ModelTrainer(result).initiate_model_training()


@task
def retrain_model(result, cfg):
    """
    Task to initiate model retraining using the ModelTrainer component.

    Args:
        result: The train-test split data.
        cfg: The config for the model retraining

    Returns:
        None
    """
    ModelTrainer(result).train_and_log_model(
        cfg["model_name"], custom_params=cfg["params"]
    )
