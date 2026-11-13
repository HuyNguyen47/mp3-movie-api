import pytest
from src import MovieStorage
import pandas as pd
import main
from pathlib import Path

def test_movies_persist(client, test_storage, uploaded_movies):
    object_lst = []
    main_lst = []
    movie = MovieStorage(test_storage.db_path)
    get_movie = movie.get()
    count_movies = movie.count_movies()

    assert count_movies == 20
    assert get_movie.columns.tolist() == ["title", "release_year", "rating", "genre"]
    df = pd.read_csv("fixtures/sample_movies.csv")
    assert get_movie["title"].tolist() == df["title"].tolist()

    for col in movie.select_columns(uploaded_movies["column_names"], 100):
        object_lst.append(col["id"])
    response = client.get("/movies", params={"limit":100})
    
    for col in response.json()["data"]:
        main_lst.append(col["id"])
    assert object_lst == main_lst


def test_cache_and_processing(client, uploaded_movies, processing_body):
    response1 = client.get("/movies", params={"limit":100})
    assert response1.status_code == 200
    assert response1.json() == main.cache.get(100)

    response2 = client.get("/movies", params={"limit":1})
    assert response2.status_code == 200
    assert response2.json() == main.cache.get(1)

    response3 = client.get("/movies", params={"limit":100})
    assert response3.status_code == 200
    assert response3.json() == main.cache.get(100)

    response4 = client.post("/movies/process", json=processing_body)
    assert response4.status_code == 200
    assert response4.json()["validation_rows_removed"] == 0
    assert response4.json()["cleaning_report"]["rows_before"] == 20
    assert response4.json()["cleaning_report"]["rows_after"] == 16
    assert main.cache.get(1) == None
    assert main.cache.get(100) == None

    response5_id_lst = []
    id_lst = []
    response5_title_lst = []
    title_lst = []
    response5 = client.get("/movies", params={"limit":100})
    response5.json()["total_rows"] == 16
    for col in response5.json()["data"]:
        response5_id_lst.append(col["id"])
    for col in main.cache.get(100)["data"]:
        id_lst.append(col["id"])
    for col in response5.json()["data"]:
        response5_title_lst.append(col["title"])
    for col in main.cache.get(100)["data"]:
        title_lst.append(col["title"])

    assert response5_title_lst == title_lst
    assert response5_id_lst == id_lst

    response5.json() == main.cache.get(100)


def test_cache_hit_skips_database(client, uploaded_movies, monkeypatch):
    first = client.get("/movies", params={"limit": 100})
    assert first.status_code == 200

    def fail_if_called(*args, **kwargs):
        pytest.fail("A cache hit should not query the database")
    

    monkeypatch.setattr(main.storage, "select_columns", fail_if_called)
    monkeypatch.setattr(main.storage, "count_movies", fail_if_called)

    second = client.get("/movies", params={"limit": 100})
    assert second.status_code == 200
    assert second.json() == first.json()
