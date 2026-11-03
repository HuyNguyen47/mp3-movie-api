# data_processor.py
import logging
import pandas as pd

logger = logging.getLogger(__name__)

def remove_duplicates(df):
    """Remove duplicate rows."""
    before = df.copy()
    df = df.drop_duplicates()    
    logger.debug(f"remove_duplicates: {len(before)} -> {len(df)}")
    return df

def handle_missing(df, axis="rows"):
    """Drop rows or columns containing missing values."""
    before = df.copy()
    if axis not in ["rows", "columns"]:
        logger.error(f"Unsupported axis: {axis}")
        raise ValueError
    if axis == "rows":
        df = df.dropna()
    else:
        df = df.dropna(axis=1)
    logger.debug(f"handle_missing: {len(before)} -> {len(df)}")
    return df

def remove_outliers(df, columns, method, threshold):
    """Remove outliers from the specified numeric columns."""
    if method in ["iqr", "zscore"]:
        before = len(df)
        missing_columns = [col for col in columns if col not in df.columns]
        is_not_numeric = [col for col in columns if not pd.api.types.is_numeric_dtype(df[col])]
        if missing_columns:
            logger.warning("A configured column does not exist")
        if is_not_numeric:
            logger.warning("A configured column is not numeric")
        for col in columns:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            lower = q1 - threshold * iqr
            upper = q3 + threshold * iqr
            mean = df[col].mean()
            std = df[col].std()
            z_scores = (df[col] - mean) / std
            if method == 'iqr':
                df = df[(df[col] >= lower) & (df[col] <= upper)]
            else:
                df = df[z_scores.abs() <= 3]
        logger.debug(f"Method: {method}, Threshold: {threshold}, Rows removed: {before - len(df)}")
        return df
    else:
        logger.error("Method does not exist")
        raise ValueError
    
 

def process_data(df, config):
    """Apply the processing steps enabled in the configuration."""
    #check if removing duplic is enabled, if so then we run remov..()
    if config["processing"]["remove_duplicates"]:
        df = remove_duplicates(df)
    if config["processing"]["missing"]["enabled"]:
        df = handle_missing(df, axis=config["processing"]["missing"]["axis"])
    if config["processing"]["outliers"]["enabled"]:
        df = remove_outliers(df, columns=config["processing"]["outliers"]["columns"], method=config["processing"]["outliers"]["method"], threshold=config["processing"]["outliers"]["threshold"])
    return df


def create_cleaning_report(df_before, df_after):
    """Return a dictionary summarizing the cleaning results."""
    return {'rows_before': df_before.shape[0], 'rows_after': df_after.shape[0], 'rows_removed': df_before.shape[0] - df_after.shape[0], 'columns_before': df_before.shape[1], 'columns_after': df_after.shape[1], 'columns_removed': df_before.shape[1] - df_after.shape[1]}
