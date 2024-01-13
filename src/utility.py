"""
Utility Module.

Provides utility functions

Example:
    from src.utility import get_cfg()
    config_file = get_cfg("./.cfg/logger.yaml")
    print(f"The logger path is: {config_file['path']}")
"""
import yaml


def get_cfg(path, encoding="utf-8"):
    """
    Loads a YAML configuration file from the specified path.

    Args:
        path (str): The path to the YAML configuration file.
        encoding (str, optional): The encoding to use when reading the file. Defaults to "utf-8".

    Returns:
        dict: The YAML configuration file.
    """

    with open(path, encoding=encoding) as file:
        return yaml.safe_load(file)
