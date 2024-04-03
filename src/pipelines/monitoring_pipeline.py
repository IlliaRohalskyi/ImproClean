"""Prefect pipeline for data monitoring and anomaly detection.

This Prefect flow performs the following tasks:

1. Loads reference data for validation.
2. Loads prediction data.
3. Selects relevant columns from both datasets.
4. Validates the prediction data against the reference data.
5. Performs data cleaning if necessary.
6. Creates drift reports if drift is detected.
7. Sends email notifications using the provided SMTP server details.
8. Cleans up temporary files.

This pipeline is designed to be run periodically to monitor the
quality and consistency of predictions.
"""
import os
import shutil

from prefect import flow, task

from src.components.data_ingestion import DataIngestion
from src.components.data_transformation import DataTransformation
from src.components.data_validation import DataValidation
from src.components.email_service import EmailService
from src.utility import get_cfg, get_root


@task
def load_reference_data():
    """
    Task to load reference data for validation.

    Returns:
    - ref_data (pandas.DataFrame): Reference data for validation.
    """
    return DataIngestion().initiate_data_ingestion()


@task
def load_predictions_data(cfg):
    """
    Task to load the table containing predictions

    Args:
    - cfg (dict): Configuration containing predictions table to be loaded

    Returns:
    - pred_data (pandas.DataFrame): DataFrame with predictions
    """
    table_name = cfg["historical_data"]
    return DataIngestion().get_sql_table(table_name)


@task
def delete_data(cfg):
    """
    Task to delete prediction data.

    Args:
    - cfg (dict): Configuration containing table to be deleted

    Returns:
    - None
    """
    table_name = cfg["historical_data"]
    DataIngestion().delete_data(table_name)


@task
def select_data(data):
    """
    Task to select relevant data columns for dataframe.

    Args:
    - data (pandas.DataFrame): data from which columns are to be selected.

    Returns:
    - selected_data (pandas.DataFrame): Selected data.
    """

    return DataTransformation().select_data(data)


@task
def validate_data(pred_df, ref_df):
    """
    Task to validate prediction data against reference data.

    Performs checks for training data quality and prediction data consistency.
    Cleans data if necessary based on the identified issues.

    Args:
    - pred_df (pandas.DataFrame): DataFrame containing predictions.
    - ref_df (pandas.DataFrame): Reference data for validation.

    Returns:
        - validated_pred (pandas.DataFrame): Cleaned prediction data.
        - validated_ref (pandas.DataFrame): Cleaned reference data (if applicable).
        - validation_checks (list): List of validation checks that triggered data cleaning.
    """
    train_checks = DataValidation().check_training_data(ref_df)
    if train_checks:
        ref_df = DataTransformation().clean_data(ref_df, train_checks)
    prediction_checks = DataValidation().check_prediction_data(pred_df, ref_df)
    if "nan_imputable" in prediction_checks or "duplicates" in prediction_checks:
        pred_df = DataTransformation().clean_data(pred_df, prediction_checks)
    return pred_df, ref_df, prediction_checks


@task
def create_reports(validation_checks, pred_df, ref_df):
    """
    Task to create drift reports if drift is detected in the data.

    Args:
    - validation_checks (list): List of validation checks that triggered data cleaning.
    - pred_df (pandas.DataFrame): Cleaned prediction data.
    - ref_df (pandas.DataFrame): Cleaned reference data.
    """
    if "drift_detected" in validation_checks:
        DataValidation().create_drift_reports(pred_df, ref_df)


@task
def alert(smtp_server, smtp_port):
    """
    Task to send email notifications using the provided SMTP server details.

    Args:
    - smtp_server (str): Address of the SMTP server.
    - smtp_port (int): Port number of the SMTP server.
    """
    EmailService().send_email(smtp_server, smtp_port)


@task
def cleanup():
    """
    Task to clean up temporary files generated during the pipeline execution.

    This task removes the drift reports folder after the pipeline finishes.
    """
    drift_reports_folder = DataValidation().validation_config["drift_reports_folder"]
    path = os.path.join(get_root(), drift_reports_folder)
    shutil.rmtree(path)


@flow(name="monitoring_pipeline")
def monitoring_pipeline(cfg, smtp_server="smtp.office365.com", smtp_port=587):
    """
    Prefect flow to monitor data quality and detect anomalies in predictions.

    Args:
        cfg (dict): Configuration dictionary containing pipeline parameters.
        smtp_server (str, optional): Address of the SMTP server for email notifications.
        smtp_port (int, optional): Port number of the SMTP server. Defaults to 587.
    """
    ref_data = load_reference_data()
    pred_data = load_predictions_data(cfg)
    delete_data(cfg)
    ref_data_selected = select_data(ref_data)
    pred_data_selected = select_data(pred_data)
    validated_pred, validated_ref, checks = validate_data(
        pred_data_selected, ref_data_selected
    )
    create_reports(checks, validated_pred, validated_ref)
    alert(smtp_server, smtp_port)
    cleanup()


if __name__ == "__main__":
    configuration = get_cfg("pipelines/monitoring_pipeline.yaml")
    monitoring_pipeline(configuration)
