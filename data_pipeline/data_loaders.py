from pathlib import Path
import logging
import pandas as pd
import json
import yaml

logger = logging.getLogger(__name__)

def load_csv(filepath):
    """Load a CSV file into a DataFrame."""
    df = pd.read_csv(filepath)
    logger.info(f"Loaded CSV file: {filepath} ({len(df)} rows)")
    return df
    

def load_json(filepath):
    """Load a JSON file into a Python object (dict or list)."""
    with open(filepath, "r") as f:
        data = json.load(f)
    logger.info(f"Loaded JSON file: {filepath}")
    return data

def load_yaml(filepath):
    """Load a YAML file into a Python object."""
    with open(filepath, "r") as f:
        config = yaml.safe_load(f)
    logger.info(f"Loaded YAML file: {filepath}")
    return config

def load_data(filepath):
    """Load a file based on its extension."""
    path = Path(filepath)
    if path.suffix == ".csv":
        return load_csv(path)
    elif path.suffix == ".json":
        return load_json(path)
    elif path.suffix == ".yaml":
        return load_yaml(path)
    else:
        logging.error(f"Unsupported file format: {path.suffix}")
        raise ValueError
