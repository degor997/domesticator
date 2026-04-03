"""Tests for ProxyManager."""

from shared.proxy.manager import ProxyManager


class TestProxyManager:
    def test_empty(self):
        pm = ProxyManager()
        assert pm.list_all() == []
        assert pm.get_next() is None

    def test_add(self):
        pm = ProxyManager()
        assert pm.add("http://proxy1:8080") is True
        assert pm.list_all() == ["http://proxy1:8080"]

    def test_add_duplicate(self):
        pm = ProxyManager()
        pm.add("http://proxy1:8080")
        assert pm.add("http://proxy1:8080") is False

    def test_remove(self):
        pm = ProxyManager()
        pm.add("http://proxy1:8080")
        assert pm.remove("http://proxy1:8080") is True
        assert pm.list_all() == []

    def test_remove_nonexistent(self):
        pm = ProxyManager()
        assert pm.remove("http://proxy1:8080") is False

    def test_rotation(self):
        pm = ProxyManager()
        pm.add("http://proxy1:8080")
        pm.add("http://proxy2:8080")
        first = pm.get_next()
        second = pm.get_next()
        third = pm.get_next()
        assert first == "http://proxy1:8080"
        assert second == "http://proxy2:8080"
        assert third == "http://proxy1:8080"

    def test_single_proxy_rotation(self):
        pm = ProxyManager()
        pm.add("http://proxy1:8080")
        assert pm.get_next() == "http://proxy1:8080"
        assert pm.get_next() == "http://proxy1:8080"
