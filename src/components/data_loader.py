"""
This module provides a function to load data from a DVC remote repository.
"""

import os
import subprocess


def load_dvc():
    """
    Loads data from a DVC remote repository.
    """
    aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
    s3_bucket_name = os.environ.get("DVC_BUCKET_NAME")

    # Execute the aws configure command with the provided parameters
    subprocess.call(["aws", "configure", "set", "aws_access_key_id", aws_access_key_id])
    subprocess.call(
        ["aws", "configure", "set", "aws_secret_access_key", aws_secret_access_key]
    )
    subprocess.call(
        ["dvc", "remote", "add", "--default", "datastore", f"s3://{s3_bucket_name}"]
    )

    subprocess.run(["dvc", "pull"], check=True)


if __name__ == "__main__":
    load_dvc()
