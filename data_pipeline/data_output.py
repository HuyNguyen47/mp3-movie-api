# src/data_output.py
import logging
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)

def save_data(df, filepath):
    """Save a DataFrame as a CSV file."""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(filepath, index=False)
    logger.debug(f"Number of rows saved: {len(df)}, Output path: {filepath}")
    return filepath















    # if isinstance(df, dict):
    #     if "Data" in df and isinstance(df["Data"], list):
    #         df_to_save = pd.DataFrame(df["Data"])
    #     else:
    #         df_to_save = pd.DataFrame([df])
    # else:
    #     df_to_save = df
