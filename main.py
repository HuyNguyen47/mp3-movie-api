import io
import json
import logging
from pathlib import Path
import pandas as pd
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from src import log_requests, ProcessingReport, ProcessConfig, DatasetInfo, DatasetStorage, HealthResponse, setup_logging
from data_pipeline import create_cleaning_report, process_data, validate_dataframe

setup_logging(verbose=True)
logger = logging.getLogger(__name__)

app = FastAPI(title="Data Processing API", version="1.0.0")

app.middleware("http")(log_requests)

storage = DatasetStorage()

@app.get("/health", response_model=HealthResponse)
def health_check():
    """Return the application status and version."""
    return {"status": "ok", "version": "1.0.0"}

@app.post("/upload", response_model=DatasetInfo)
async def upload_dataset(file: UploadFile = File(...)):
    """Read and store a CSV upload."""
    if Path(file.filename).suffix.lower() != ".csv":
        logger.warning(f"Unsupported file format: {Path(file.filename).suffix.lower()}")
        raise HTTPException(status_code=400, detail="Non-CSV file Uploaded")
    
    contents = await file.read()

    try:
        df = pd.read_csv(io.BytesIO(contents))
    except (pd.errors.EmptyDataError,pd.errors.ParserError,UnicodeDecodeError) as error:
        logger.warning(f"Cannot read CSV: {error}")
        raise HTTPException(status_code=400, detail="Cannot read the uploaded CSV")

    file_id = storage.save(df, file.filename)
    logger.info(f"Filename {file.filename}, (ID {file_id}) saved, {len(df)} rows")
    return DatasetInfo(
            id=file_id,
            filename=file.filename,
            rows=df.shape[0], 
            columns=df.shape[1],
            column_names=list(df.columns),
    )



@app.get("/datasets/{dataset_id}")
def get_dataset(dataset_id: int, limit: int = Query(default=100, ge=1)):
    """Return up to limit rows from a stored dataset."""
    result = storage.get(dataset_id)
    if result is None:
        logger.warning(f"Dataset not found: {dataset_id}")
        raise HTTPException(status_code=404, detail="Not found")

    record = json.loads(result.head(limit).to_json(orient="records"))   
    logger.info(f"Retrieved dataset: id={dataset_id}, returned rows={len(result)}")
    return {"id":dataset_id, 
            "data":record,
            "rows":len(record)
            }

@app.post(
    "/datasets/{dataset_id}/process",
    response_model=ProcessingReport
)
def process_dataset(dataset_id: int, config: ProcessConfig):
    """Validate and process a stored dataset using MP1 functions."""
    # TODO: retrieve, validate, process, report, update, and return.
    result = storage.get(dataset_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Not found")
    numeric_cols = config.validation.numeric_columns
    required_cols = config.validation.required_columns
    if numeric_cols is None:
        raise HTTPException(status_code=400, detail="Not numeric")
    try:
        validate_df = validate_dataframe(result, required_cols, numeric_cols)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    rows_removed = len(result) - len(validate_df)
    request_model_dict = config.model_dump()
    process_df = process_data(validate_df, request_model_dict)
    cleaning_report = create_cleaning_report(validate_df, process_df)
    storage.update(dataset_id, process_df)
    logger.info(f"Processed dataset: id={dataset_id}, validation_removed={rows_removed}, rows_before={len(result)}, rows_after={len(process_df)}")
    return {"id": dataset_id, 
            "validation_rows_removed": rows_removed,
            "cleaning_report": cleaning_report}
