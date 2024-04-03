"""
This module provides data validation capabilities for both training and prediction scenarios.
It can be employed to assess data quality
"""
import logging
import os
import warnings
from typing import List

from evidently.metric_preset import (
    DataDriftPreset,
    DataQualityPreset,
    TargetDriftPreset,
)
from evidently.report import Report
from scipy.stats import kruskal, ks_2samp

from src.errors.data_validation_errors import ColumnsDiffError, DtypeDiffError, NanError
from src.utility import get_cfg, get_root


class DataValidation:
    """
    Data validation class.

    This class provides a method for data validation tasks.

    Attributes:
        validation_config (dict):
        The configuration settings for data validation tasks
    """

    def __init__(self):
        """
        Initialize the DataValidation instance.

        Attributes:
            self.validation_config (dict): Configuration settings for data validation tasks.
        """
        self.validation_config = get_cfg("components/data_validation.yaml")

    def _check_nan(self, data) -> str:
        """
        Checks for NaN values in the provided DataFrame.

        Args:
            data (pandas.DataFrame): The DataFrame to be checked.

        Returns:
            str: Indicates the presence of NaN values:
                - "nan_nonimputable": If NaN count exceeds the threshold
                - "nan_imputable": If NaN count is present but below the threshold
                - None: If there are no NaN values
        """
        logging.info("Checking for NaN values")
        nan_thresh = self.validation_config["nan_thresh"]
        nan_present = False
        df = data.drop_duplicates()
        for column in df:
            nan_count = df[column].isna().sum()
            if nan_count / len(df) > nan_thresh:
                return "nan_nonimputable"
            if nan_count != 0:
                nan_present = True

        if nan_present:
            return "nan_imputable"

        return None

    def check_training_data(self, train_df) -> List[str]:
        """
        Validates training data.

        Args:
            train_df (pandas.DataFrame): The training DataFrame.

        Returns:
            List[str]: A list of validation issues identified, including:
                - "nan_imputable": If NaN count is present but below the threshold
                - "duplicates": If the DataFrame contains duplicate rows
        """
        logging.info("Validating training data")

        validation_issues = []
        nan_message = self._check_nan(train_df)

        if nan_message == "nan_nonimputable":
            logging.error("NanError encountered")
            raise NanError
        if nan_message is not None:
            validation_issues.append(nan_message)

        duplicates_present = train_df.duplicated().any()
        if duplicates_present:
            validation_issues.append("duplicates")
        return validation_issues

    def check_prediction_data(self, pred_df, train_df) -> List[str]:
        """
        Validates prediction data.

        Args:
            pred_df (pandas.DataFrame): The prediction DataFrame.
            train_df (pandas.DataFrame): The training DataFrame.

        Returns:
            List[str]: A list of validation issues identified, including:
                - "nan_imputable": If NaN count is present but below the threshold
        """
        logging.info("Validating prediction data")

        validation_issues = []
        nan_message = self._check_nan(pred_df)

        duplicates_present = pred_df.duplicated().any()
        if duplicates_present:
            validation_issues.append("duplicates")

        if nan_message == "nan_nonimputable":
            logging.error("NanError encountered")
            raise NanError
        validation_issues.append(nan_message)
        if not all(pred_df.columns == train_df.columns):
            logging.error("ColumnsDiffError encountered")
            raise ColumnsDiffError(pred_df, train_df)
        if not all(pred_df.dtypes == train_df.dtypes):
            logging.error("DtypeDiffError encountered")
            raise DtypeDiffError

        drift_detected = self.check_data_drift(pred_df, train_df)
        if drift_detected:
            validation_issues.append("drift_detected")
        return validation_issues

    def check_data_drift(self, pred_df, train_df):
        """
        Checks for data drift between the prediction data and the training data.
        If present, warning is raised.

        Args:
            pred_df (pd.DataFrame): The prediction data to be compared against the training data.
            train_df (pd.DataFrame): The training data to be used as the reference data.

        Returns:
            bool: True if drift is present, false otherwise
        """

        drift_thresh = self.validation_config["drift_thresh"]
        cat_cols = self.validation_config["cat_cols"]
        num_cols = [col for col in pred_df.columns if col not in cat_cols]
        drift_present = False
        for column in num_cols:
            _, p_value = ks_2samp(pred_df[column], train_df[column])
            if p_value < drift_thresh:
                warnings.warn(
                    f"Numerical drift detected in column {column}. Proceeding..."
                )
                logging.info("Numerical drift detected in column %s", column)
                drift_present = True

        if cat_cols != [None]:
            for column in cat_cols:
                _, p_value = kruskal(pred_df[column], train_df[column])
                if p_value < drift_thresh:
                    warnings.warn(
                        f"Categorical drift detected in column {column}. Proceeding..."
                    )
                    logging.info("Categorical drift detected in column %s", column)
                    drift_present = True

        return drift_present

    def create_drift_reports(self, pred_df, train_df):
        """
        Generate drift reports comparing prediction data to training data.

        Args:
            pred_df (pandas.DataFrame): DataFrame containing the prediction data.
            train_df (pandas.DataFrame): DataFrame containing the training data.

        Returns:
            None
        """
        report = Report(
            metrics=[
                DataQualityPreset(),
                DataDriftPreset(),
                TargetDriftPreset(),
            ]
        )

        report.run(current_data=pred_df, reference_data=train_df)

        drift_reports_folder = self.validation_config["drift_reports_folder"]

        dir_path = os.path.join(get_root(), drift_reports_folder)
        os.makedirs(dir_path, exist_ok=True)
        file_path = os.path.join(dir_path, "drift_report.html")
        report.save_html(file_path)
