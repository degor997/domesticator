"""Tests for crawler extraction logic."""

from unittest.mock import AsyncMock

from shared.browser.crawler import _extract_field, extract_data
from shared.config.models import FieldExtractor, HostConfig


def _mock_element(text: str | None = None, attr: str | None = None):
    el = AsyncMock()
    el.text_content = AsyncMock(return_value=text)
    el.get_attribute = AsyncMock(return_value=attr)
    return el


def _mock_page(elements: dict[str, list | None] = None):
    page = AsyncMock()
    elements = elements or {}

    async def query_selector(sel):
        els = elements.get(sel, [])
        return els[0] if els else None

    async def query_selector_all(sel):
        return elements.get(sel, [])

    page.query_selector = query_selector
    page.query_selector_all = query_selector_all
    return page


class TestExtractField:
    async def test_simple_text(self):
        page = _mock_page({".price": [_mock_element(text="$99.99")]})
        extractor = FieldExtractor(selectors=[".price"], required=True)
        result = await _extract_field(page, extractor)
        assert result == "$99.99"

    async def test_fallback_selector(self):
        page = _mock_page({".price-new": [_mock_element(text="$50")]})
        extractor = FieldExtractor(selectors=[".price-old", ".price-new"])
        result = await _extract_field(page, extractor)
        assert result == "$50"

    async def test_attribute_selector(self):
        el = _mock_element(attr="29.99")
        page = _mock_page({"meta[property='og:price']": [el]})
        extractor = FieldExtractor(
            selectors=[{"value": "meta[property='og:price']", "attribute": "content"}]
        )
        result = await _extract_field(page, extractor)
        assert result == "29.99"

    async def test_not_found(self):
        page = _mock_page({})
        extractor = FieldExtractor(selectors=[".nonexistent"])
        result = await _extract_field(page, extractor)
        assert result is None

    async def test_multiple_values(self):
        els = [_mock_element(text="img1.jpg"), _mock_element(text="img2.jpg")]
        page = _mock_page({".gallery img": els})
        extractor = FieldExtractor(selectors=[".gallery img"], multiple=True)
        result = await _extract_field(page, extractor)
        assert result == ["img1.jpg", "img2.jpg"]


class TestExtractData:
    async def test_full_extraction(self):
        page = _mock_page({
            ".price": [_mock_element(text="₺ 299,99")],
            ".old-price": [_mock_element(text="₺ 399,99")],
        })
        config = HostConfig(
            field_extractors={
                "price": FieldExtractor(
                    selectors=[".price"],
                    required=True,
                    transforms=["clean_text", "text_to_price"],
                ),
                "old_price": FieldExtractor(
                    selectors=[".old-price"],
                    required=False,
                    transforms=["clean_text", "text_to_price"],
                ),
            }
        )
        result = await extract_data(page, config)
        assert result["price"] == 29999
        assert result["old_price"] == 39999

    async def test_missing_required_field(self):
        page = _mock_page({})
        config = HostConfig(
            field_extractors={
                "price": FieldExtractor(selectors=[".price"], required=True),
            }
        )
        result = await extract_data(page, config)
        assert result["price"] is None

    async def test_missing_optional_field(self):
        page = _mock_page({})
        config = HostConfig(
            field_extractors={
                "old_price": FieldExtractor(selectors=[".old-price"], required=False),
            }
        )
        result = await extract_data(page, config)
        assert result["old_price"] is None
