"""
Test Data Validation.

This module contains test cases for the DataValidation class
from the data_validation module.
"""
from test.test_utility import (
    create_cat_col,
    create_duplicated_data,
    create_nan_data,
    create_synthetic_data,
)

import pytest

from src.components.data_validation import DataValidation
from src.errors.data_validation_errors import ColumnsDiffError, DtypeDiffError, NanError
from src.utility import get_cfg


@pytest.fixture(name="data_validation_object")
def fixture_validation_object():
    """
    Fixture for DataValidation Object.

    This fixture creates and returns an instance of the DataValidation class.
    Changes the path of the config file to the test one

    Returns:
        DataValidation: An instance of the DataValidation class.
    """
    data_transformation_object = DataValidation()
    data_transformation_object.validation_config = get_cfg(
        "test/unit/test_data_validation.yaml"
    )
    return data_transformation_object


def test_train_validation(data_validation_object):
    """
    Test Train Validation Functionality.

    This test case verifies the functionality of the check_training_data method
    in the DataValidation class.

    Args:
        data_validation_object (DataValidation): An instance of the DataValidation class
    """
    synthetic_data = create_synthetic_data()
    clean_check = data_validation_object.check_training_data(synthetic_data)
    assert len(clean_check) == 0, "Validation checks are present for clean data"

    duplicated_data = create_duplicated_data(synthetic_data)
    duplicated_check = data_validation_object.check_training_data(duplicated_data)
    assert duplicated_check == ["duplicates"], "Test failed for data with duplicates"

    nan_data_nonimputable = create_nan_data(nan_percent=0.3)

    with pytest.raises(NanError):
        data_validation_object.check_training_data(nan_data_nonimputable)

    nan_data_imputable = create_nan_data()
    duplicated_nan_data = create_duplicated_data(nan_data_imputable)

    duplicated_nan_checks = data_validation_object.check_training_data(
        duplicated_nan_data
    )
    assert duplicated_nan_checks == [
        "nan_imputable",
        "duplicates",
    ], "Test failed with data that has duplicates and nan values"


def test_prediction_validation(data_validation_object):
    """
    Test Prediction Validation Functionality.

    This test case verifies the functionality of the check_prediction_data method
    in the DataValidation class.

    Args:
        data_validation_object (DataValidation): An instance of the DataValidation class
    """
    nan_data_nonimputable = create_nan_data(nan_percent=0.3)
    synthetic_data = create_synthetic_data()
    with pytest.raises(NanError):
        data_validation_object.check_prediction_data(
            nan_data_nonimputable, synthetic_data
        )

    diff_cols_data = synthetic_data.rename(
        columns={synthetic_data.columns[0]: "diff_col_name"}
    )
    with pytest.raises(ColumnsDiffError):
        data_validation_object.check_prediction_data(diff_cols_data, synthetic_data)

    diff_dtype_data = synthetic_data.copy()
    diff_dtype_data.iloc[:, 2] = diff_dtype_data.iloc[:, 2].astype(str)
    with pytest.raises(DtypeDiffError):
        data_validation_object.check_prediction_data(diff_dtype_data, synthetic_data)

    nan_data_imputable = create_nan_data() + 1000

    nan_data_imputable = create_cat_col(nan_data_imputable, [0.65, 0.3, 0.05])
    synthetic_data = create_cat_col(synthetic_data, [0.3, 0.05, 0.65])

    with pytest.warns(UserWarning, match="drift detected in column"):
        val_issues = data_validation_object.check_prediction_data(
            nan_data_imputable, synthetic_data
        )
    print(val_issues)
    assert "nan_imputable" in val_issues, "NaN imputable case failed"
