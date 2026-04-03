"""Tests for /v0/proxies routes."""



class TestProxiesRoutes:
    async def test_list_empty(self, client):
        resp = await client.get("/v0/proxies")
        assert resp.status_code == 200
        assert resp.json() == {"proxies": []}

    async def test_add_proxy(self, client):
        resp = await client.post("/v0/proxies/add", json={"proxy_url": "http://proxy1:8080"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "added"

    async def test_add_duplicate_proxy(self, client):
        await client.post("/v0/proxies/add", json={"proxy_url": "http://proxy2:8080"})
        resp = await client.post("/v0/proxies/add", json={"proxy_url": "http://proxy2:8080"})
        assert resp.status_code == 409

    async def test_list_after_add(self, client):
        await client.post("/v0/proxies/add", json={"proxy_url": "http://proxy3:8080"})
        resp = await client.get("/v0/proxies")
        assert "http://proxy3:8080" in resp.json()["proxies"]

    async def test_delete_proxy(self, client):
        await client.post("/v0/proxies/add", json={"proxy_url": "http://proxy4:8080"})
        resp = await client.delete("/v0/proxies/http://proxy4:8080")
        assert resp.status_code == 200

    async def test_delete_nonexistent_proxy(self, client):
        resp = await client.delete("/v0/proxies/http://nonexistent:8080")
        assert resp.status_code == 404
