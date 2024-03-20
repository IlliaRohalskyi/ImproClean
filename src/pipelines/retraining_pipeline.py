"""
Module for defining a Prefect flow to orchestrate a machine learning retraining pipeline.

This module includes tasks for data ingestion, transformation, validation,
train-test split, and model retraining.
"""

from prefect import flow

from src.pipelines.common.training_tasks import (
    get_data,
    retrain_model,
    select_data,
    train_test_split,
    validate_data,
)
from src.utility import get_cfg


@flow(name="retrain_pipeline")
def retraining_pipeline():
    """
    Prefect flow to orchestrate the entire retraining pipeline.

    Returns:
        None
    """
    cfg = get_cfg("pipelines/retraining_pipeline.yaml")
    data = get_data()
    selected_data = select_data(data)
    validated_data = validate_data(selected_data)
    train_test_split_data = train_test_split(validated_data)
    retrain_model(train_test_split_data, cfg)


if __name__ == "__main__":
    retraining_pipeline()
