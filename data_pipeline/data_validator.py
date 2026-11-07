# src/data_validator.py
import logging
import pandas as pd

logger = logging.getLogger(__name__)

def validate_dataframe(df, required_columns, numeric_columns):
    """Validate the DataFrame and return valid data.
    required_columns: a list of column names that must exist.
    numeric_columns: a list of column names whose values should be
    numeric.
    """
    before = len(df)
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        logger.error(f"Missing Columns: {",".join(missing_columns)}")
        raise ValueError(f"{len(missing_columns)} columns missing")
    for col in numeric_columns:
        invalid_rows = []
        logged_warning = False
        for i, value in df[col].items():
            if pd.notna(value):
                try:
                    float(value)
                except ValueError:
                    invalid_rows.append(i)
                    if not logged_warning:
                        logger.warning("Cannot convert some invalid numeric values into number")
                        logged_warning = True
        
        df = df.drop(index=invalid_rows)

        df[col] = pd.to_numeric(df[col])
    logger.debug(f"Number of valid rows: {len(df)}, Number of removed rows: {before - len(df)}")
    return df
