import os
from test.test_utility import upload_data
from unittest.mock import patch

import pytest

from src.pipelines.monitoring_pipeline import monitoring_pipeline
from src.utility import get_cfg, get_root


@patch("src.components.email_service.smtplib.SMTP")
def test_monitoring_integration(_):
    test_data_path = os.path.join(
        get_root(),
        "test",
        "synthetic_data",
        "unformatted",
        "synthetic_unformatted.xlsx",
    )
    cfg = get_cfg("test/integration/test_monitoring_pipeline.yaml")
    upload_data(test_data_path, cfg["historical_data"])
    monitoring_pipeline(cfg, smtp_server="localhost", smtp_port=1025)
