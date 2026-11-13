mp3-movie-api is similar to mp2 api but stores one movie collection in a sqlite table and uses sql to filter records. src/database.py creates the connections and the movie table and src/storage.py stores and queries the movie collection using sql. The data folder contains the sqlite database which has files that validates and processes the data. Fixtures contains the csv dataset and the src folder is the package. src/cache.py has a class that utilizes caching with sql storage and processing. main.py is where the endpoints are which has the upload_movies, get_movies, query_movies, and process_movies endpoints. The command for testing is python -m pytest tests -v and starting the API is python -m uvicorn main:app --reload. A sample processing request using sample_movie.csv is 

{
  "validation": {
    "required_columns": [
      "title", "release_year", "rating", "genre"
    ],
    "numeric_columns": [
      "release_year", "rating"
    ]
  },
  "processing": {
    "remove_duplicates": true,
    "missing": {
      "enabled": true,
      "axis": "rows"
    },
    "outliers": {
      "enabled": true,
      "columns": [
        "rating"
      ],
      "method": "iqr",
      "threshold": 1.5
        }
    }
}

which results in 

{
  "validation_rows_removed": 0,
  "cleaning_report": {
    "rows_before": 20,
    "rows_after": 16,
    "rows_removed": 4,
    "columns_before": 4,
    "columns_after": 4,
    "columns_removed": 0
  }
}
