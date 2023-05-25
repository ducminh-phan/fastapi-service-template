async def test_items(client):
    response = await client.get("/items/count")
    assert response.status_code == 200
    assert response.json()["count"] == 0

    response = await client.post("/items")
    assert response.status_code == 200

    response = await client.get("/items/count")
    assert response.status_code == 200
    assert response.json()["count"] == 1
