"""
Model Loader Script

This script provides functions to download machine learning models
from the MLFlow model registry.
"""

import ast
from typing import List, Tuple

import mlflow


# pylint: disable=R0903
class Predictor:
    """
    A class for making ensemble predictions using MLFlow models and weights.
    """

    def __init__(self, models, weights):
        """
        Initialize the Predictor.

        Args:
            models (dict): Dictionary of MLFlow models.
            weights (dict): Dictionary of model weights.
        """
        if len(models) == 0 or len(weights) == 0:
            raise ValueError("Models and weights must not be empty")

        if len(models) != len(weights):
            raise ValueError("Number of models must be equal to the number of weights")

        self.models = models
        self.weights = weights

    def predict(self, input_data):
        """
        Make ensemble predictions.

        Args:
            input_data: Input data for prediction.

        Returns:
            float: Ensemble prediction.
        """
        if not all(model_name in self.models for model_name in self.weights):
            raise ValueError(
                "All models in weights must be present in the models dictionary"
            )

        ensemble_prediction = 0.0

        for model_name, model in self.models.items():
            weight = self.weights.get(model_name, 0.0)
            model_prediction = model.predict(input_data)
            ensemble_prediction += weight * model_prediction

        return ensemble_prediction


def get_models(model_names: Tuple[str] = ("xgb", "rf")) -> Predictor:
    """
    Load models from the MLFlow model registry.

    Args:
        model_names (Tuple[str]): Names of the MLFlow models to load.

    Returns:
        Predictor: An instance of the Predictor class.
    """
    models = {}
    weights = []

    for model_name in model_names:
        latest_versions = mlflow.tracking.MlflowClient().get_latest_versions(
            name=model_name
        )

        if latest_versions:
            latest_version = latest_versions[0]
            model = (
                mlflow.xgboost.load_model(f"runs:/{latest_version.run_id}/{model_name}")
                if model_name == "xgb"
                else mlflow.sklearn.load_model(
                    f"runs:/{latest_version.run_id}/{model_name}"
                )
            )
            models[model_name] = model

            try:
                weights_str = (
                    mlflow.tracking.MlflowClient()
                    .get_run(latest_version.run_id)
                    .data.params["weights"]
                )
                weights_dict = ast.literal_eval(weights_str)
                weights.append(weights_dict)

            except:  # pylint: disable=W0702
                pass

    weight = check_weights(weights, model_names)

    return Predictor(models, weight)


def check_weights(weights: List[dict], model_names: Tuple[str]) -> dict:
    """
    Check and adjust weights.

    Args:
        weights (List[dict]): List of weight dictionaries.
        model_names (Tuple[str]): Names of the MLFlow models.

    Returns:
        dict: Adjusted weights.
    """
    if len(weights) > 1 and all(
        all(abs(weights[i][key] - weights[j][key]) < 1e-5 for key in weights[i])
        for i in range(len(weights))
        for j in range(i + 1, len(weights))
    ):
        weight = weights[0]
    else:
        num_models = len(model_names)
        weight = {model: 1 / num_models for model in model_names}

    return weight


if __name__ == "__main__":
    a = get_models()
    print(a.models, a.weights)
