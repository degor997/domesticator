"""Tests for /v0/config/hosts routes."""



class TestHostsRoutes:
    async def test_get_all_hosts(self, client):
        resp = await client.get("/v0/config/hosts")
        assert resp.status_code == 200
        data = resp.json()
        assert "trendyol.com" in data

    async def test_get_host(self, client):
        resp = await client.get("/v0/config/hosts/trendyol.com")
        assert resp.status_code == 200
        data = resp.json()
        assert "default" in data

    async def test_get_host_not_found(self, client):
        resp = await client.get("/v0/config/hosts/nonexistent.com")
        assert resp.status_code == 404

    async def test_get_strategies(self, client):
        resp = await client.get("/v0/config/hosts/trendyol.com/strategies")
        assert resp.status_code == 200
        data = resp.json()
        assert "default" in data["strategies"]

    async def test_add_host_config(self, client):
        resp = await client.post(
            "/v0/config/hosts/newhost.com?strategy=default",
            json={
                "field_extractors": {
                    "title": {"selectors": ["h1"], "required": False, "transforms": ["clean_text"]}
                }
            },
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "created"

    async def test_add_duplicate(self, client):
        await client.post(
            "/v0/config/hosts/dup.com?strategy=default",
            json={"field_extractors": {}},
        )
        resp = await client.post(
            "/v0/config/hosts/dup.com?strategy=default",
            json={"field_extractors": {}},
        )
        assert resp.status_code == 409

    async def test_update_host_config(self, client):
        await client.post(
            "/v0/config/hosts/upd.com?strategy=default",
            json={"field_extractors": {}},
        )
        resp = await client.put(
            "/v0/config/hosts/upd.com?strategy=default",
            json={"field_extractors": {}, "wait_until": "load"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "updated"

    async def test_update_nonexistent(self, client):
        resp = await client.put(
            "/v0/config/hosts/nonexistent.com?strategy=default",
            json={"field_extractors": {}},
        )
        assert resp.status_code == 404

    async def test_delete_host_config(self, client):
        await client.post(
            "/v0/config/hosts/del.com?strategy=default",
            json={"field_extractors": {}},
        )
        resp = await client.delete("/v0/config/hosts/del.com?strategy=default")
        assert resp.status_code == 200
        assert resp.json()["status"] == "deleted"

    async def test_delete_nonexistent(self, client):
        resp = await client.delete("/v0/config/hosts/nonexistent.com?strategy=default")
        assert resp.status_code == 404

    async def test_frozen_config_post(self, client, config_store):
        from shared.config.models import HostConfig
        frozen_cfg = HostConfig(field_extractors={}, frozen=True)
        await config_store.add_config("frozen.com", "default", frozen_cfg)

        resp = await client.post(
            "/v0/config/hosts/frozen.com?strategy=default",
            json={"field_extractors": {}},
        )
        assert resp.status_code == 423

    async def test_frozen_config_put(self, client, config_store):
        from shared.config.models import HostConfig
        frozen_cfg = HostConfig(field_extractors={}, frozen=True)
        await config_store.add_config("frozen2.com", "default", frozen_cfg)

        resp = await client.put(
            "/v0/config/hosts/frozen2.com?strategy=default",
            json={"field_extractors": {}},
        )
        assert resp.status_code == 423

    async def test_frozen_config_delete(self, client, config_store):
        from shared.config.models import HostConfig
        frozen_cfg = HostConfig(field_extractors={}, frozen=True)
        await config_store.add_config("frozen3.com", "default", frozen_cfg)

        resp = await client.delete("/v0/config/hosts/frozen3.com?strategy=default")
        assert resp.status_code == 423
