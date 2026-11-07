import logging
import sqlite3

import pandas as pd

from .database import get_connection, initialize_database

logger = logging.getLogger(__name__)
MOVIE_COLUMNS = ["title", "release_year", "rating", "genre"]

class MovieStorage:
    def __init__(self, db_path="data/movies.db"):
        self.db_path = db_path
        initialize_database(self.db_path)

    def save(self, df):
        """Replace all movie rows in one transaction."""
        # TODO: Convert missing values to Python None for SQL NULL.
        # DELETE the old rows, then INSERT all rows from df.
        # Commit only after all inserts succeed; roll back on SQLite errors.
        # Close the connection in finally. Log the saved row count at DEBUG.
        connection = get_connection(self.db_path)

        #replace na with None
        df = df.where(pd.notna(df), None)
        #convrert df to list-of tp
        list_of_tuples = df.to_records(index=False).tolist()
        try:

            #delete
            connection.execute("DELETE FROM movies")

            #inser
            sql_statement = "INSERT INTO movies (title, release_year, rating, genre) VALUES (?, ?, ?, ?)"
            cursor = connection.execute(sql_statement, list_of_tuples)
            logger.debug(f"Saved row count: {len(cursor)}")
            connection.commit() 
        except sqlite3.Error:
            connection.rollback()
            raise
        finally:
            connection.close()


    def get(self):
        """Return the four movie columns as a DataFrame, ordered by id."""
        # TODO: SELECT the four fields, fetch rows, and create the DataFrame.
        # Return a DataFrame with columns=MOVIE_COLUMNS,
        # so the column names are preserved even when the query returns no rows.
        connection = get_connection(self.db_path)
        try:
            sql_statement = """SELECT
            title, release_year, rating, genre FROM movies 
            ORDER BY id"""
            rows = connection.execute(sql_statement).fetchall()
            df = pd.DataFrame(rows, columns=MOVIE_COLUMNS)
            return df
        finally:
            connection.close()

    def select_columns(self, columns, limit=5):
        """Return id plus the requested movie columns, ordered by id."""
        if not columns:
            logger.error("Select at least one column")
            raise ValueError("Select at least one column")
        for column in columns:
            if column not in MOVIE_COLUMNS:
                logger.error(f"Unsupported column: {column}")
                raise ValueError(f"Unsupported column: {column}")
        selected_columns = ", ".join(["id"] + columns)
        connection = get_connection(self.db_path)
        try:
            # TODO: SELECT selected_columns from movies, ordered by id.
            # Use a placeholder for limit; fetch the rows.
            # Return a list of dictionaries and log at DEBUG.
            sql_statement = """
            SELECT ? FROM movies
            ORDER BY id LIMIT ?
            """
            rows = connection.execute(sql_statement, (selected_columns, limit)).fetchall()
            out = [dict(row) for row in rows]
            logger.debug(f"{len(out)} movies")
            return out
        finally:
            connection.close()

    def count_movies(self):
        """Return the number of stored movies using SQL COUNT(*)."""
        connection = get_connection(self.db_path)
        try:
            sql_statement = "SELECT COUNT(*) AS total FROM movies"
            row = connection.execute(sql_statement).fetchone()
            return row["total"]
        finally:
            connection.close()

    def query_movies(self, columns, min_rating, limit):
        """Return selected fields from matching movies using SQL."""
        # TODO: validate columns as in select_columns().
        # SELECT id plus those columns and filter by minimum rating.
        # Sort by rating DESC then id ASC, and apply limit.
        # Return dictionaries and log the selected columns and row count at DEBUG.
        if not columns:
            logger.error("Select at least one column")
            raise ValueError("Select at least one column")
        for column in columns:
            if column not in MOVIE_COLUMNS:
                logger.error(f"Unsupported column: {column}")
                raise ValueError(f"Unsupported column: {column}")
        connection = get_connection(self.db_path)
        try:
            sql_statement = """
                SELECT * FROM movies
                WHERE rating >= ? ORDER BY rating DESC, id ASC LIMIT ?
                """
            rows = connection.execute(sql_statement, (min_rating, limit)).fetchall()
            out = [dict(row) for row in rows]
            logger.debug(f"Selected columns: {columns}, row count: {len(out)}")
            return out
        finally:
            connection.close()






























# import logging

# logger = logging.getLogger(__name__)

# class MovieStorage:
#     def __init__(self):
#         self._store = {}
#         self._counter = 0

#     def save(self, df, filename):
#         """Store a copy of the data and return a new integer ID."""
#         self._counter += 1
#         dataset_id = self._counter
#         self._store[dataset_id] = {"filename": filename, "data": df.copy()}
#         logger.debug(f"Stored dataset: id={dataset_id}, rows={len(df)}")
#         return dataset_id
    
#     def get(self, dataset_id):
#         """Return a copy of the stored DataFrame, or None."""
#         item = self._store.get(dataset_id)
#         if item is None:
#             logger.debug(f"Dataset not found: id={dataset_id}")
#             return None
#         df = item["data"]
#         logger.debug(f"Retrieved dataset: id={dataset_id}, rows={len(df)}")
#         return df.copy()

#     def get_metadata(self, dataset_id):
#         """Return the dataset metadata, or None."""
#         filename = self._store[dataset_id]["filename"]
#         df = self._store[dataset_id]["data"]
#         return {"id": dataset_id, "filename": filename, "rows": len(df), "columns": df.shape[1], "column_names": list(df.columns)}


#     def update(self, dataset_id, df):
#         """Replace an existing dataset; return True, or False if
#         missing."""
#         if dataset_id not in self._store:
#             return False
#         self._store[dataset_id]["data"] = df.copy()
#         logger.debug(f"Updated dataset: id={dataset_id}, rows={len(self._store[dataset_id]["data"])}")
#         return True

#     def clear(self):
#         """Clear all data and reset the ID counter."""
#         self._store.clear()
#         self._counter = 0
