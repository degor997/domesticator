"""Tests for base routes (/, /ping, /health)."""



class TestBaseRoutes:
    async def test_index(self, client):
        resp = await client.get("/")
        assert resp.status_code == 200
        assert "text/html" in resp.headers.get("content-type", "")

    async def test_ping(self, client):
        resp = await client.get("/ping")
        assert resp.status_code == 200
        assert resp.json() == {"ping": "pong"}

    async def test_health(self, client):
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
