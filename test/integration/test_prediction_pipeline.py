import os
from test.test_utility import upload_data

import pytest

from src.pipelines.prediction_pipeline import prediction_pipeline
from src.utility import get_cfg, get_root


def test_pred_integration():
    test_data_path = os.path.join(
        get_root(),
        "test",
        "synthetic_data",
        "unformatted",
        "synthetic_unformatted.xlsx",
    )
    cfg = get_cfg("test/integration/test_prediction_pipeline.yaml")
    upload_data(test_data_path, cfg["prediction_table"])
    prediction_pipeline(cfg)
