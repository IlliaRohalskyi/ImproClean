"""
Model Loader Script

This script provides functions to download machine learning models
from the MLFlow model registry
"""

from typing import Tuple

import mlflow


def get_models(model_names: Tuple[str] = ("xgb", "rf")):
    """
    Load models from the MLFlow model registry.

    Args:
        model_names (Tuple[str]): Names of the MLFlow models to load.

    Returns:
        List: A list of model objects which stores the loaded model
    """
    models = []
    for model_name in model_names:
        latest_versions = mlflow.tracking.MlflowClient().get_latest_versions(
            name=model_name
        )

        if latest_versions:
            latest_version = latest_versions[0]
            print(latest_version)
            model = (
                mlflow.xgboost.load_model(f"runs:/{latest_version.run_id}/{model_name}")
                if model_name == "xgb"
                else mlflow.sklearn.load_model(
                    f"runs:/{latest_version.run_id}/{model_name}"
                )
            )
            models.append(model)
    return model
