"""
Model Trainer Module

This module contains the implementation of a class, ModelTrainer, which is responsible for
training and evaluating machine learning models using Optuna for hyperparameter
optimization and MLflow for tracking experiments.

Classes:
    ModelTrainer: A class for training and evaluating machine learning models.

Usage:
    Instantiate the ModelTrainer class with TrainTestData, call initiate_model_training()
    to train models using hyperparameter optimization, and log results and artifacts to MLflow.
"""
import os
import shutil
import subprocess
import sys

import matplotlib.pyplot as plt
import mlflow
import numpy as np
import optuna
import pandas as pd
from evidently import ColumnMapping
from evidently.metric_preset import RegressionPreset
from evidently.report import Report
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import KFold
from xgboost import XGBRegressor

from src.components.data_transformation import TrainTestData
from src.errors.model_training_errors import (
    EnsembleMetricsError,
    PlotError,
    ReportError,
    TrainLogError,
)
from src.logger import logging
from src.utility import get_cfg, get_root


class ModelTrainer:
    """
    Class for training and evaluating machine learning models.
    """

    def __init__(self, train_test_data: TrainTestData):
        """
        Initialize the ModelTrainer.

        Args:
            train_test_data (TrainTestData): Data for training and testing.
        """
        self.current_model_name = None
        self.data = train_test_data
        self.git_hash = self._get_git_hash()
        self.cfg = get_cfg("components/model_training.yaml")
        self.explainability_path = os.path.join(
            get_root(), self.cfg["explainability_path"]
        )

    def _train_model(self, model_name, params):
        """
        Train a machine learning model.

        Args:
            model_name (str): Name of the model.
            params (dict): Hyperparameters for the model to be used.

        Returns:
            model: Trained machine learning model.
        """
        logging.info("Training model")

        if model_name == "rf":
            model = RandomForestRegressor(**params)
        elif model_name == "xgb":
            model = XGBRegressor(**params)
        else:
            raise ValueError(f"Unsupported model name: {model_name}")

        model.fit(self.data.x_train, self.data.y_train)
        return model

    def objective(self, trial):
        """
        Objective function for Optuna hyperparameter optimization.

        Args:
            trial (optuna.Trial): Optuna trial object.

        Returns:
            float: Mean absolute error (MAE) for the model.
        """
        model_name = self.current_model_name

        mae_list = []
        k_fold = KFold(n_splits=5, shuffle=True, random_state=42)

        for train_idx, val_idx in k_fold.split(self.data.x_train, self.data.y_train):
            if model_name == "xgb":
                model = XGBRegressor(
                    n_estimators=trial.suggest_int("n_estimators", 5, 200),
                    max_depth=trial.suggest_int("max_depth", 3, 200),
                    learning_rate=trial.suggest_float("learning_rate", 0.001, 0.3),
                    subsample=trial.suggest_float("subsample", 0.1, 1.0),
                    colsample_bytree=trial.suggest_float("colsample_bytree", 0.1, 1.0),
                    gamma=trial.suggest_float("gamma", 0, 10),
                    min_child_weight=trial.suggest_int("min_child_weight", 1, 20),
                    reg_alpha=trial.suggest_float("reg_alpha", 0, 1),
                    reg_lambda=trial.suggest_float("reg_lambda", 0, 1),
                )
            elif model_name == "rf":
                model = RandomForestRegressor(
                    n_estimators=trial.suggest_int("n_estimators", 5, 200),
                    max_depth=trial.suggest_int("max_depth", 3, 200),
                    min_samples_split=trial.suggest_int("min_samples_split", 2, 30),
                    min_samples_leaf=trial.suggest_int("min_samples_leaf", 1, 15),
                    max_features=trial.suggest_float("max_features", 0.1, 1),
                    bootstrap=trial.suggest_categorical("bootstrap", [True, False]),
                )
            else:
                raise ValueError(f"Unsupported model name: {model_name}")

            x_train_fold, x_val_fold = (
                self.data.x_train[train_idx],
                self.data.x_train[val_idx],
            )
            y_train_fold, y_val_fold = (
                self.data.y_train[train_idx],
                self.data.y_train[val_idx],
            )

            model.fit(x_train_fold, y_train_fold)
            predictions = model.predict(x_val_fold)

            mae = mean_absolute_error(y_val_fold, predictions, multioutput="raw_values")

            target_to_minimize = mae[0]

            mae_list.append(target_to_minimize)

        return np.mean(mae_list)

    def _get_git_hash(self):
        """
        Get the Git hash of the current commit.

        Returns:
            str: Git hash.
        """
        try:
            logging.info("Getting git hash")

            git_hash = (
                subprocess.check_output(["git", "rev-parse", "HEAD"])
                .strip()
                .decode("utf-8")
            )
            return git_hash
        except subprocess.CalledProcessError as error_message:
            logging.error(
                f"Error: Failed to retrieve Git hash. "
                f"Command returned {error_message.returncode}: {error_message.output}"
            )
            return "Unknown"

    def initiate_model_training(self):
        """
        Initialize the model training process.
        """
        logging.info("Starting model training")

        models = self.cfg["models"]

        with mlflow.start_run():
            mlflow.log_param("git_hash", self.git_hash)

            best_models = []
            best_maes = []

            for model_name in models:
                self.current_model_name = model_name

                sampler = optuna.samplers.TPESampler(
                    seed=42, n_startup_trials=self.cfg["startup_trials"]
                )
                study = optuna.create_study(direction="minimize", sampler=sampler)
                logging.info("Starting hyperparameter tuning")
                study.optimize(
                    self.objective,
                    n_trials=self.cfg["total_trials"],
                    show_progress_bar=True,
                )

                mlflow.log_metric(
                    f"{model_name}_val_microbiology_mae", study.best_value
                )
                best_model, best_mae = self.train_and_log_model(model_name, study=study)

                best_models.append(best_model)
                best_maes.append(best_mae)

            if len(models) > 1:
                self.log_ensemble_metrics(best_maes, best_models)

    def feature_importance_plot(self, model, model_name):
        """
        Generate and save a feature importance plot.

        Args:
            model: Trained machine learning model.
            model_name (str): Name of the model.
        """
        try:
            logging.info("Executing feature importance plots")

            feature_importances = model.feature_importances_
            n_features = len(feature_importances)

            plt.figure(figsize=(10, 12))
            plt.barh(range(n_features), feature_importances, align="center")

            plt.yticks(np.arange(n_features), self.data.feature_names)

            plt.xlabel("Feature Importance")
            plt.ylabel("Feature")

            plt.title(f"{model_name} Model - Feature Importance")

            plt.tight_layout()

            os.makedirs(self.explainability_path, exist_ok=True)
            plt.savefig(
                os.path.join(
                    self.explainability_path,
                    f"{model_name}_feature_importance.png",
                )
            )
            plt.close()
        except Exception as error_message:
            logging.error(
                f"Error encountered when producing a plot with error message: {error_message}"
            )
            raise PlotError(error_message, sys) from error_message

    def log_ensemble_metrics(self, best_maes, best_models):
        """
        Log ensemble metrics to MLflow.

        Args:
            best_maes (list): List of best mean absolute errors.
            best_models (list): List of best trained models.
        """
        try:
            logging.info("logging ensemble metrics")

            test_ensemble_predictions = np.zeros_like(self.data.y_test)
            train_ensemble_predictions = np.zeros_like(self.data.y_train)
            total_weight = sum(1 / mae for mae in best_maes)
            weights = [1 / mae / total_weight for mae in best_maes]
            mlflow.log_params({"weights": weights})

            for model, weight in zip(best_models, weights):
                train_predictions = model.predict(self.data.x_train)
                train_ensemble_predictions += weight * train_predictions
                test_predictions = model.predict(self.data.x_test)
                test_ensemble_predictions += weight * test_predictions

            self.regression_report(
                train_ensemble_predictions, test_ensemble_predictions, "ensemble"
            )
            mlflow.log_artifacts(
                self.explainability_path,
                artifact_path="explainability",
            )
            shutil.rmtree(self.explainability_path)

            ensemble_mae = mean_absolute_error(
                self.data.y_test, test_predictions, multioutput="raw_values"
            )

            ensemble_r2 = r2_score(
                self.data.y_test, test_predictions, multioutput="raw_values"
            )

            mlflow.log_metric("ensemble_test_mae_microbiology", ensemble_mae[0])
            mlflow.log_metric("ensemble_test_mae_energy", ensemble_mae[1])

            mlflow.log_metric("ensemble_test_r2_microbiology", ensemble_r2[0])
            mlflow.log_metric("ensemble_test_r2_energy", ensemble_r2[1])
        except Exception as error_message:
            logging.error(
                f"Logging ensemble metrics failed with error: {error_message}"
            )
            raise EnsembleMetricsError(error_message, sys) from error_message

    def train_and_log_model(self, model_name, study=None, custom_params=None) -> tuple:
        """
        Train a model on best parameters from optuna study, or retrain with custom params.
        Log metrics and artifacts to MLflow afterward.

        Args:
            model_name (str): Name of the model.
            study (optuna.Study): Optuna study object. (Optional)
            custom_params (dict): Custom model parameters. (Optional)

        Returns:
            tuple: Tuple containing the best trained model and its MAE from study,
            if called with custom_params, returns trained model and NAN tuple
        """
        try:
            logging.info("Training model")

            if custom_params is not None and study is not None:
                raise ValueError("Both, study and custom_params were provided")
            if study is not None:
                params = study.best_params
            elif custom_params is not None:
                params = custom_params

            else:
                raise ValueError("Either study or custom_params must be provided.")

            params_with_prefix = {
                f"{model_name}_{key}": value for key, value in params.items()
            }
            mlflow.log_params(params_with_prefix)

            best_model = self._train_model(model_name, params)

            if model_name == "xgb":
                mlflow.xgboost.log_model(
                    xgb_model=best_model,
                    artifact_path=f"models/{model_name}",
                    registered_model_name=model_name,
                )
            elif model_name == "rf":
                mlflow.sklearn.log_model(
                    sk_model=best_model,
                    artifact_path=f"models/{model_name}",
                    registered_model_name=model_name,
                )
            else:
                raise ValueError(f"Unsupported model name: {model_name}")

            test_predictions = best_model.predict(self.data.x_test)

            train_predictions = best_model.predict(self.data.x_train)

            self.regression_report(train_predictions, test_predictions, model_name)

            mae = mean_absolute_error(
                self.data.y_test, test_predictions, multioutput="raw_values"
            )

            r2 = r2_score(self.data.y_test, test_predictions, multioutput="raw_values")

            mlflow.log_metric(f"{model_name}_test_mae_microbiology", mae[0])
            mlflow.log_metric(f"{model_name}_test_mae_energy", mae[1])

            mlflow.log_metric(f"{model_name}_test_r2_microbiology", r2[0])
            mlflow.log_metric(f"{model_name}_test_r2_energy", r2[1])

            if self.data.feature_names is not None:
                self.feature_importance_plot(best_model, model_name)

                mlflow.log_artifacts(
                    self.explainability_path,
                    artifact_path="explainability",
                )
                shutil.rmtree(self.explainability_path)
            return (best_model, study.best_value if study is not None else None)

        except Exception as error_message:
            logging.error(
                f"Training and logging model failed with error: {error_message}"
            )
            raise TrainLogError(error_message, sys) from error_message

    def regression_report(self, train_pred, test_pred, model_name):
        """
        This method is responsible for generating regression report and saving it

        Args:
            test_pred (np.ndarray): The test predictions (inverse transformed)
            train_pred (np.ndarray): The train predictions (inverse transformed)
            model_name (str): The model name that is being used
        """
        try:
            os.makedirs(self.explainability_path, exist_ok=True)
            targets = ["Microbiology", "Energy Consumption"]

            for i, target in enumerate(targets):
                curr_target_name = target
                curr_train_pred = train_pred[:, i]
                curr_test_pred = test_pred[:, i]
                column_mapping = ColumnMapping()
                column_mapping.target = curr_target_name
                column_mapping.prediction = "Prediction"

                ref = pd.DataFrame(
                    {
                        curr_target_name: self.data.y_train[:, i],
                        "Prediction": curr_train_pred,
                    }
                )
                cur = pd.DataFrame(
                    {
                        curr_target_name: self.data.y_test[:, i],
                        "Prediction": curr_test_pred,
                    }
                )

                reg_performance_report = Report(metrics=[RegressionPreset()])

                reg_performance_report.run(
                    reference_data=ref, current_data=cur, column_mapping=column_mapping
                )
                reg_performance_report.save_html(
                    os.path.join(
                        self.explainability_path,
                        f"{model_name}_{curr_target_name}_performance_report.html",
                    )
                )

        except Exception as error_message:
            logging.error(f"Regression report failed with error: {error_message}")
            raise ReportError(error_message, sys) from error_message
