import io
import json
import logging
from pathlib import Path
import pandas as pd
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from src import MovieCache, MovieStorage, MovieUploadInfo, MovieDataResponse, MovieProcessingReport, log_requests, ProcessingReport, ProcessConfig, DatasetInfo, HealthResponse, setup_logging
from src.storage import MOVIE_COLUMNS
from data_pipeline import create_cleaning_report, process_data, validate_dataframe

setup_logging(verbose=True)
logger = logging.getLogger(__name__)

app = FastAPI(title="Data Processing API", version="1.0.0")

app.middleware("http")(log_requests)

storage = MovieStorage()

cache = MovieCache()

@app.get("/health", response_model=HealthResponse)
def health_check():
    """Return the application status and version."""
    return {"status": "ok", "version": "1.0.0"}

@app.post("/upload", response_model=MovieUploadInfo)
async def upload_movies(file: UploadFile = File(...)):
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

    if df.columns is not MOVIE_COLUMNS and df.empty:
        raise HTTPException(status_code=400, detail="Columns are not exactly MOVIE_COLUMNS or dataframe is empty")
    df = df[MOVIE_COLUMNS]

    storage.save(df)
    cache.invalidate()
    logger.info(f"Uploaded movies: filename={file.filename}, rows={len(df)}")
    return MovieUploadInfo(
            filename=file.filename,
            rows=df.shape[0], 
            columns=df.shape[1],
            column_names=list(df.columns),
    )



@app.get("/movies", response_model=MovieDataResponse)
def get_movies(limit: int = Query(default=100, ge=1)):
    """Return up to limit rows from a stored dataset."""
    cached = cache.get(limit)
    if cached is not None:
        logger.info(f"Listed movies: rows={len(cached)}") 
        return cached
    df = storage.get()
    if df.empty:
        returned_df = {"data": [], "total_rows": 0}
        cache.set(limit, returned_df)
        return returned_df
    rows = storage.count_movies()
    result = storage.select_columns(df.columns.tolist(), limit)
    logger.info(f"Number of stored movies: {rows}")
    returned_df = {"data": result, "total_rows": rows}
    cache.set(limit,returned_df)
    return returned_df


@app.get("/movies/search", response_model=list[dict])
def query_movies(
    columns: list[str] = Query(default=["title"]),
    min_rating: float = Query(default=0, ge=0, le=10),
    limit: int = Query(default=100, ge=1)
    ):
    try:
        result = storage.query_movies(columns, min_rating, limit)
    except ValueError:
        raise HTTPException(status_code=400, detail="Cannot query movies")
    logger.info(f"Queried movies: columns={columns}, min_rating={min_rating}, returned_rows={len(result)}")
    return result

@app.post(
    "/movies/process",
    response_model=MovieProcessingReport
)
def process_dataset(config: ProcessConfig):
    """Validate and process a stored dataset using MP1 functions."""
    df = storage.get()
    if df.empty:
        raise HTTPException(status_code=404, detail="Not found")
    numeric_cols = config.validation.numeric_columns
    required_cols = config.validation.required_columns
    if numeric_cols is None:
        raise HTTPException(status_code=400, detail="Not numeric")
    try:
        validate_df = validate_dataframe(df, required_cols, numeric_cols)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    rows_removed = len(df) - len(validate_df)
    request_model_dict = config.model_dump()
    process_df = process_data(validate_df, request_model_dict)
    cleaning_report = create_cleaning_report(validate_df, process_df)
    storage.save(process_df)
    cache.invalidate()
    return {"validation_rows_removed": rows_removed,
            "cleaning_report": cleaning_report}
