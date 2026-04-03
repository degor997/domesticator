"""Tests for MemoryConfigStore."""

import pytest

from shared.config.memory_store import MemoryConfigStore
from shared.config.models import FieldExtractor, HostConfig


@pytest.fixture
async def store():
    return MemoryConfigStore()


@pytest.fixture
def sample_config():
    return HostConfig(
        field_extractors={
            "price": FieldExtractor(
                selectors=[".price"],
                required=True,
                transforms=["clean_text", "text_to_price"],
            )
        }
    )


class TestMemoryConfigStore:
    async def test_empty_store(self, store):
        result = await store.get_all()
        assert result == {}

    async def test_add_and_get(self, store, sample_config):
        ok = await store.add_config("example.com", "default", sample_config)
        assert ok is True
        config = await store.get_config("example.com", "default")
        assert config is not None
        assert config.field_extractors["price"].required is True

    async def test_add_duplicate(self, store, sample_config):
        await store.add_config("example.com", "default", sample_config)
        ok = await store.add_config("example.com", "default", sample_config)
        assert ok is False

    async def test_get_host(self, store, sample_config):
        await store.add_config("example.com", "default", sample_config)
        host = await store.get_host("example.com")
        assert host is not None
        assert "default" in host

    async def test_get_host_not_found(self, store):
        host = await store.get_host("nonexistent.com")
        assert host is None

    async def test_get_strategies(self, store, sample_config):
        await store.add_config("example.com", "default", sample_config)
        await store.add_config("example.com", "mobile", sample_config)
        strategies = await store.get_strategies("example.com")
        assert sorted(strategies) == ["default", "mobile"]

    async def test_update_config(self, store, sample_config):
        await store.add_config("example.com", "default", sample_config)
        new_config = HostConfig(field_extractors={})
        ok = await store.update_config("example.com", "default", new_config)
        assert ok is True
        config = await store.get_config("example.com", "default")
        assert config.field_extractors == {}

    async def test_update_nonexistent(self, store, sample_config):
        ok = await store.update_config("example.com", "default", sample_config)
        assert ok is False

    async def test_delete_strategy(self, store, sample_config):
        await store.add_config("example.com", "default", sample_config)
        ok = await store.delete_config("example.com", "default")
        assert ok is True
        config = await store.get_config("example.com", "default")
        assert config is None

    async def test_delete_host(self, store, sample_config):
        await store.add_config("example.com", "default", sample_config)
        ok = await store.delete_config("example.com")
        assert ok is True
        host = await store.get_host("example.com")
        assert host is None

    async def test_delete_nonexistent(self, store):
        ok = await store.delete_config("nonexistent.com", "default")
        assert ok is False

    async def test_load_from_file(self):
        store = MemoryConfigStore()
        await store.load_from_file()
        all_configs = await store.get_all()
        assert "trendyol.com" in all_configs
        assert "amazon.com.tr" in all_configs
        assert "n11.com" in all_configs
        assert "idefix.com" in all_configs
