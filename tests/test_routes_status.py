"""Tests for /v0/status route."""



class TestStatusRoute:
    async def test_status(self, client):
        resp = await client.get("/v0/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["version"] == "1.0.0"
        assert data["browser"] is True

    async def test_status_fields(self, client):
        resp = await client.get("/v0/status")
        data = resp.json()
        assert "status" in data
        assert "version" in data
        assert "browser" in data
