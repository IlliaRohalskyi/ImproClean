"""
Module for defining a Prefect flow to orchestrate a machine learning training pipeline.

This module includes tasks for data ingestion, transformation, validation,
train-test split, and model training.
"""
from prefect import flow

from src.pipelines.common.training_tasks import (
    get_data,
    select_data,
    train_model,
    train_test_split,
    validate_data,
)


@flow(name="train_pipeline")
def training_pipeline():
    """
    Prefect flow to orchestrate the entire training pipeline.

    Returns:
        None
    """
    data = get_data()
    selected_data = select_data(data)
    validated_data = validate_data(selected_data)
    train_test_split_data = train_test_split(validated_data)
    train_model(train_test_split_data)


if __name__ == "__main__":
    training_pipeline()
