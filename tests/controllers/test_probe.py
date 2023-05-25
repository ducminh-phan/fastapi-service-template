async def test_ping(client):
    response = await client.post("/pings")
    assert response.status_code == 405

    response = await client.get("/pings")
    assert response.status_code == 200
