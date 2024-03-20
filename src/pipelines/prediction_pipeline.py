"""
Module for defining a Prefect flow to orchestrate a machine learning prediction pipeline.

This module coordinates tasks for data ingestion, transformation, validation,
model loading, prediction generation, and writing results. It leverages components
from the src.components package to streamline the workflow.

Key tasks within this module:

- load_model: Loads trained machine learning models according to configuration.
- load_reference_data: Fetches reference data for prediction and validation.
- get_pred_data: Retrieves data for prediction from the designated table.
- select_data: Selects relevant features or subsets from the prediction data.
- validate_data: Performs data quality checks and applies necessary cleaning.
- get_predictions: Generates predictions using the loaded model on validated data.
- write_predictions: Writes the model's predictions to a specified table.
"""
import pandas as pd
from prefect import flow, task

from src.components.data_ingestion import DataIngestion
from src.components.data_transformation import DataTransformation
from src.components.data_validation import DataValidation
from src.components.model_loader import get_models
from src.utility import get_cfg


@task
def load_model(cfg):
    """
    Task to load machine learning models based on the provided configuration.
    If default, load ensemble

    Args:
    - cfg (dict): Configuration containing model names.

    Returns:
    - models (Predictor): predictor class with ensemble predict functionality.
    """
    model_names = cfg["model_names"]
    if model_names != "default":
        model_names = tuple(model_names)
        return get_models(model_names)
    return get_models()


@task
def load_reference_data():
    """
    Task to load reference data for validation.

    Returns:
    - ref_data (pandas.DataFrame): Reference data for validation.
    """
    return DataIngestion().initiate_data_ingestion()


@task
def get_pred_data(cfg):
    """
    Task to retrieve prediction data from the SQL table based on configuration.

    Args:
    - cfg (dict): Configuration containing prediction table information.

    Returns:
    - pred_data (pandas.DataFrame): Prediction data.
    """
    prediction_table = cfg["prediction_table"]
    return DataIngestion().get_sql_table(prediction_table)


@task
def select_data(ingested_pred):
    """
    Task to select relevant data columns for prediction.

    Args:
    - ingested_pred (pandas.DataFrame): Ingested prediction data.

    Returns:
    - selected_pred (pandas.DataFrame): Selected prediction data.
    """

    return DataTransformation().select_data(ingested_pred, select_target=False)


@task
def validate_data(selected_pred, ref_data):
    """
    Task to validate prediction data.

    Args:
    - selected_pred (pandas.DataFrame): Selected prediction data.
    - ref_data (pandas.DataFrame): Reference data for validation.

    Returns:
    - validated_data (pandas.DataFrame): Validated prediction data.
    """
    validation_checks = DataValidation().check_prediction_data(selected_pred, ref_data)
    if validation_checks:
        return DataTransformation().clean_data(selected_pred, validation_checks)
    return selected_pred


@task
def get_predictions(ensemble_model, validated_data):
    """
    Task to get predictions using the ensemble model.

    Args:
    - ensemble_model (Predictor): Ensemble machine learning model.
    - validated_data (pandas.DataFrame): Validated prediction data.

    Returns:
    - predictions (numpy.ndarray): Array of predictions.
    """
    return ensemble_model.predict(validated_data)


@task
def write_predictions(cfg, predictions, ingested_data, ref_data):
    """
    Task to write predictions to a specified table.

    Args:
    - cfg (dict): Configuration containing table information.
    - predictions (numpy.ndarray): Array of predictions.
    - ingested_data (pandas.DataFrame): Ingested prediction data.
    - ref_data (pandas.DataFrame): Reference data.

    Returns:
    - None
    """
    table_name = cfg["write_table"]
    index_col = cfg["index_col"]
    mapping = ref_data.columns.str.startswith(("Red KBE", "Energie"))
    pred_col_names = ref_data.columns[mapping]
    print(predictions, pred_col_names)
    preds_df = pd.DataFrame(predictions, columns=pred_col_names)
    dataframe = pd.concat(
        [
            ingested_data[[index_col]],
            preds_df,
            ingested_data.drop([index_col], axis=1),
        ],
        axis=1,
    )

    DataIngestion().write_data(dataframe, table_name)


@task
def delete_data(cfg):
    """
    Task to delete prediction data.

    Args:
    - cfg (dict): Configuration containing prediction table information.

    Returns:
    - None
    """
    table_name = cfg["prediction_table"]
    DataIngestion().delete_data(table_name)


@flow(name="prediction_pipeline")
def prediction_pipeline(config):
    """
    Prefect flow for orchestrating a machine learning prediction pipeline.

    Args:
    - cfg (dict): Configuration containing pipeline settings.

    Returns:
    - None
    """
    loaded_model = load_model(config)
    ref_data = load_reference_data()
    pred_data = get_pred_data(config)
    delete_data(config)
    selected_pred = select_data(pred_data)
    selected_ref = select_data(ref_data)
    validated_data = validate_data(selected_pred, selected_ref)
    predictions = get_predictions(loaded_model, validated_data)
    write_predictions(config, predictions, pred_data, ref_data)


if __name__ == "__main__":
    configuration = get_cfg("pipelines/prediction_pipeline.yaml")
    prediction_pipeline(configuration)
