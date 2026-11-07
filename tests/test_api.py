def test_upload_csv(client, sample_csv_bytes):
    response = client.post("/upload", files={"file": ("sample_data.csv", sample_csv_bytes, "text/csv")})
    data_response = response.json()
    assert response.status_code == 200
    assert data_response["rows"] == 6
    assert data_response["columns"] == 2 
    assert data_response["id"] > 0

def test_process_and_retrieve(client, uploaded_dataset_id, processing_body):
    response = client.post(
        f"/datasets/{uploaded_dataset_id}/process", 
        json=processing_body
    )
    
    assert response.status_code == 200
    response_data = response.json()
    
    assert response_data["validation_rows_removed"] == 1
    
    
    report = response_data["cleaning_report"]
    assert report["rows_before"] == 5
    assert report["rows_after"] == 3


    get_response = client.get(f"/datasets/{uploaded_dataset_id}")
    
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["rows"] == 3
    id_lst = []
    score_lst = []
    for row in get_data["data"]:
        if row["student_id"] in [1, 2, 5]:
            id_lst.append(row["student_id"])
        if row["score"] in [80, 90, 85]:
            score_lst.append(row["score"])
    assert id_lst == [1, 2, 5]
    assert score_lst == [80, 90, 85]


def test_retrieve_missing_dataset(client):
    invalid = 349348
    response = client.get(f"/datasets/{invalid}")
    assert response.status_code == 404
