"""Tests for /v0/crawl route."""

from unittest.mock import AsyncMock, patch

from shared.config.models import CrawlResultItem


class TestCrawlRoute:
    async def test_crawl_basic(self, client):
        mock_result = CrawlResultItem(
            url="https://example.com",
            status="ok",
            extracted={"price": 12345},
        )
        with patch("http_api.routes.crawl.crawl_targets", new_callable=AsyncMock, return_value=[mock_result]):
            resp = await client.post(
                "/v0/crawl",
                json={
                    "targets": [{"url": "https://example.com", "require_host_config": False}]
                },
            )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["results"]) == 1
        assert data["results"][0]["status"] == "ok"

    async def test_crawl_multiple(self, client):
        results = [
            CrawlResultItem(url="https://a.com", status="ok", extracted={}),
            CrawlResultItem(url="https://b.com", status="ok", extracted={}),
        ]
        with patch("http_api.routes.crawl.crawl_targets", new_callable=AsyncMock, return_value=results):
            resp = await client.post(
                "/v0/crawl",
                json={
                    "targets": [
                        {"url": "https://a.com", "require_host_config": False},
                        {"url": "https://b.com", "require_host_config": False},
                    ]
                },
            )
        assert resp.status_code == 200
        assert len(resp.json()["results"]) == 2

    async def test_crawl_error_result(self, client):
        mock_result = CrawlResultItem(
            url="https://error.com",
            status="error",
            error="connection_failed",
        )
        with patch("http_api.routes.crawl.crawl_targets", new_callable=AsyncMock, return_value=[mock_result]):
            resp = await client.post(
                "/v0/crawl",
                json={
                    "targets": [{"url": "https://error.com", "require_host_config": False}]
                },
            )
        assert resp.status_code == 200
        assert resp.json()["results"][0]["status"] == "error"

    async def test_crawl_empty_targets(self, client):
        with patch("http_api.routes.crawl.crawl_targets", new_callable=AsyncMock, return_value=[]):
            resp = await client.post("/v0/crawl", json={"targets": []})
        assert resp.status_code == 200
        assert resp.json()["results"] == []

    async def test_crawl_with_page_content(self, client):
        mock_result = CrawlResultItem(
            url="https://example.com",
            status="ok",
            extracted={},
            page_content="<html>test</html>",
        )
        with patch("http_api.routes.crawl.crawl_targets", new_callable=AsyncMock, return_value=[mock_result]):
            resp = await client.post(
                "/v0/crawl",
                json={
                    "targets": [
                        {
                            "url": "https://example.com",
                            "require_host_config": False,
                            "with_page_content": {"type": "unrendered"},
                        }
                    ]
                },
            )
        assert resp.status_code == 200
        assert resp.json()["results"][0]["page_content"] == "<html>test</html>"
