def test_upload_csv(client, sample_csv_bytes):
    response = client.post("/upload", files={"file": ("sample_movies.csv", sample_csv_bytes, "text/csv")})
    data_response = response.json()
    assert response.status_code == 200
    assert data_response["rows"] == 20
    assert data_response["columns"] == 4 


def test_process_and_retrieve(client, processing_body):
    response = client.post(
        f"/movies/process", 
        json=processing_body
    )
    
    assert response.status_code == 200
    response_data = response.json()
    
    assert response_data["validation_rows_removed"] == 0
    
    
    report = response_data["cleaning_report"]
    assert report["rows_before"] == 18
    assert report["rows_after"] == 18



