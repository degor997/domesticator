"""Tests for Pydantic models."""


from shared.config.models import (
    CrawlRequest,
    CrawlTarget,
    FieldExtractor,
    HostConfig,
    HostStatus,
    PreAction,
    ProxyAddRequest,
)


class TestHostConfig:
    def test_defaults(self):
        cfg = HostConfig()
        assert cfg.status == HostStatus.ACTIVE
        assert cfg.frozen is False
        assert cfg.performance_mode is False
        assert cfg.wait_until == "networkidle"

    def test_with_extractors(self):
        cfg = HostConfig(
            field_extractors={
                "price": FieldExtractor(selectors=[".price"], required=True)
            }
        )
        assert "price" in cfg.field_extractors
        assert cfg.field_extractors["price"].required is True


class TestFieldExtractor:
    def test_simple_selectors(self):
        fe = FieldExtractor(selectors=[".price", ".cost"])
        assert len(fe.selectors) == 2

    def test_extended_selector(self):
        fe = FieldExtractor(
            selectors=[{"value": "meta[property='og:price']", "attribute": "content"}]
        )
        assert len(fe.selectors) == 1

    def test_with_transforms(self):
        fe = FieldExtractor(
            selectors=[".price"],
            transforms=["clean_text", {"name": "regex_extract", "pattern": r"\d+"}],
        )
        assert len(fe.transforms) == 2


class TestCrawlTarget:
    def test_minimal(self):
        t = CrawlTarget(url="https://example.com")
        assert t.require_host_config is True
        assert t.strategy == "default"

    def test_full(self):
        t = CrawlTarget(
            url="https://example.com",
            require_host_config=False,
            performance_mode=True,
            strategy="mobile",
        )
        assert t.performance_mode is True


class TestCrawlRequest:
    def test_valid(self):
        req = CrawlRequest(targets=[CrawlTarget(url="https://example.com")])
        assert len(req.targets) == 1

    def test_empty_targets(self):
        req = CrawlRequest(targets=[])
        assert len(req.targets) == 0


class TestPreAction:
    def test_wait(self):
        action = PreAction(action_type="wait", timeout=2000)
        assert action.timeout == 2000

    def test_click(self):
        action = PreAction(action_type="click", selector=".btn")
        assert action.selector == ".btn"


class TestProxyAddRequest:
    def test_valid(self):
        req = ProxyAddRequest(proxy_url="http://proxy:8080")
        assert req.proxy_url == "http://proxy:8080"
