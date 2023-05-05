def test_ping(client):
    response = client.post("/pings")
    assert response.status_code == 405

    response = client.get("/pings")
    assert response.status_code == 200
