import datetime

import mlflow
from prefect import flow, task

from src.components.data_ingestion import DataIngestion
from src.components.data_transformation import DataTransformation
from src.components.data_validation import DataValidation
from src.components.model_trainer import ModelTrainer


@task
def get_data():
    return DataIngestion().initiate_data_ingestion()


@task
def select_data(result):
    return DataTransformation().select_data(result)


@task
def validate_data(result):
    validation_checks = DataValidation().check_training_data(result)
    if validation_checks:
        return DataTransformation().clean_data(result, validation_checks)
    return result


@task
def train_test_split(result):
    return DataTransformation().create_train_test_split(result)


@task
def train_model(result):
    ModelTrainer(result).initiate_model_training()


@flow(name="train_pipeline")
def training_pipeline():
    data = get_data()
    selected_data = select_data(data)
    validated_data = validate_data(selected_data)
    train_test_split_data = train_test_split(validated_data)
    train_model(train_test_split_data)


if __name__ == "__main__":
    training_pipeline()
