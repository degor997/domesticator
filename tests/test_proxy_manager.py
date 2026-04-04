"""Tests for ProxyManager."""

import pytest

from shared.proxy.manager import ProxyManager
from shared.proxy.memory_store import MemoryProxyStore


@pytest.fixture
def pm():
    store = MemoryProxyStore()
    return ProxyManager(store)


class TestProxyManager:
    @pytest.mark.asyncio
    async def test_empty(self, pm):
        assert await pm.list_all() == []
        assert pm.get_next() is None

    @pytest.mark.asyncio
    async def test_add(self, pm):
        assert await pm.add("http://proxy1:8080") is True
        assert await pm.list_all() == ["http://proxy1:8080"]

    @pytest.mark.asyncio
    async def test_add_duplicate(self, pm):
        await pm.add("http://proxy1:8080")
        assert await pm.add("http://proxy1:8080") is False

    @pytest.mark.asyncio
    async def test_remove(self, pm):
        await pm.add("http://proxy1:8080")
        assert await pm.remove("http://proxy1:8080") is True
        assert await pm.list_all() == []

    @pytest.mark.asyncio
    async def test_remove_nonexistent(self, pm):
        assert await pm.remove("http://proxy1:8080") is False

    @pytest.mark.asyncio
    async def test_rotation(self, pm):
        await pm.add("http://proxy1:8080")
        await pm.add("http://proxy2:8080")
        first = pm.get_next()
        second = pm.get_next()
        third = pm.get_next()
        assert first == "http://proxy1:8080"
        assert second == "http://proxy2:8080"
        assert third == "http://proxy1:8080"

    @pytest.mark.asyncio
    async def test_single_proxy_rotation(self, pm):
        await pm.add("http://proxy1:8080")
        assert pm.get_next() == "http://proxy1:8080"
        assert pm.get_next() == "http://proxy1:8080"
