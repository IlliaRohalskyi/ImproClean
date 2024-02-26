"""
Integration Test for End-to-End Training Pipeline

This script defines an integration test for the end-to-end training pipeline. It tests the data
ingestion, transformation, and model training components to ensure their compatibility and
expected behavior.

Usage: Run this script with pytest to perform the integration test on the training pipeline.
"""

import os
from unittest.mock import patch

import pandas as pd

from src.components.data_ingestion import DataIngestion
from src.components.data_transformation import DataTransformation, TrainTestData
from src.components.data_validation import DataValidation
from src.components.model_trainer import ModelTrainer
from src.utility import get_cfg


def test_end_to_end_pipeline():
    """
    Integration test function.

    This function tests the data ingestion, transformation, and model training components
    to ensure their compatibility and expected behavior.
    """
    data_ingestion_object = DataIngestion()
    data_transformation_object = DataTransformation()
    data_validation_object = DataValidation()
    cfg = get_cfg("test/integration/test_train_integration.yaml")

    data_ingestion_object.ingestion_config = cfg
    data_transformation_object.transformation_config = cfg
    data_validation_object.validation_config = cfg

    ingested_data = data_ingestion_object.initiate_data_ingestion()

    selected_data = data_transformation_object.select_data(ingested_data)

    validation_checks = data_validation_object.check_training_data(selected_data)
    clean_data = data_transformation_object.clean_data(selected_data, validation_checks)

    train_test_obj = data_transformation_object.create_train_test_split(clean_data)

    model_trainer = ModelTrainer(train_test_obj)

    assert isinstance(ingested_data, pd.DataFrame)
    assert isinstance(train_test_obj, TrainTestData)
    assert isinstance(model_trainer, ModelTrainer)
