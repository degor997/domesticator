from __future__ import annotations

import logging
from typing import Any
from urllib.parse import urlparse

from playwright.async_api import Page

from shared.browser.bypass.amazon import bypass_amazon
from shared.browser.bypass.cloudflare import bypass_cloudflare
from shared.browser.bypass.stealth import apply_stealth
from shared.config.models import FieldExtractor, HostConfig, PreAction, SelectorItem
from shared.transform.pipeline import apply_transforms

logger = logging.getLogger(__name__)


async def _execute_pre_action(page: Page, action: PreAction) -> None:
    match action.action_type:
        case "wait":
            timeout = action.timeout or 1000
            await page.wait_for_timeout(timeout)
        case "wait_for_selector":
            if action.selector:
                await page.wait_for_selector(action.selector, timeout=action.timeout or 10000)
        case "click":
            if action.selector:
                await page.click(action.selector)
        case "scroll":
            direction = action.direction or "down"
            pixels = action.pixels or 300
            delta = pixels if direction == "down" else -pixels
            await page.evaluate(f"window.scrollBy(0, {delta})")
        case "input":
            if action.selector and action.text:
                await page.fill(action.selector, action.text)
        case _:
            logger.warning("Unknown pre_action type: %s", action.action_type)


async def _extract_field(page: Page, extractor: FieldExtractor) -> Any:
    for selector_raw in extractor.selectors:
        try:
            if isinstance(selector_raw, dict):
                sel = SelectorItem(**selector_raw)
            elif isinstance(selector_raw, SelectorItem):
                sel = selector_raw
            else:
                sel = SelectorItem(value=str(selector_raw))

            if extractor.multiple:
                elements = await page.query_selector_all(sel.value)
                if not elements:
                    continue
                values = []
                for el in elements:
                    if sel.attribute:
                        v = await el.get_attribute(sel.attribute)
                    else:
                        v = await el.text_content()
                    if v is not None:
                        values.append(v)
                if values:
                    return values
            else:
                element = await page.query_selector(sel.value)
                if element is None:
                    continue
                if sel.attribute:
                    value = await element.get_attribute(sel.attribute)
                else:
                    value = await element.text_content()
                if value is not None:
                    return value
        except Exception:
            logger.debug("Selector %s failed", selector_raw, exc_info=True)
            continue

    return None


async def extract_data(page: Page, config: HostConfig) -> dict[str, Any]:
    # Execute pre-actions
    for action in config.pre_actions:
        await _execute_pre_action(page, action)

    # Extract fields
    result: dict[str, Any] = {}
    for field_name, extractor in config.field_extractors.items():
        value = await _extract_field(page, extractor)
        if value is None and extractor.required:
            logger.warning("Required field %s not found", field_name)
            result[field_name] = None
            continue
        if value is not None and extractor.transforms:
            value = apply_transforms(value, extractor.transforms)
        result[field_name] = value

    return result


async def navigate_and_extract(
    page: Page,
    url: str,
    config: HostConfig | None,
    *,
    performance_mode: bool = False,
    page_content_type: str | None = None,
) -> dict[str, Any]:
    wait_until = "domcontentloaded" if performance_mode else (config.wait_until if config else "networkidle")

    await apply_stealth(page)
    await page.goto(url, wait_until=wait_until, timeout=30000)

    # Bypass detection
    hostname = (urlparse(url).hostname or "").removeprefix("www.")
    if "amazon" in hostname:
        await bypass_amazon(page)
    else:
        await bypass_cloudflare(page)

    result: dict[str, Any] = {"url": url, "status": "ok"}

    if config:
        extracted = await extract_data(page, config)
        result["extracted"] = extracted
    else:
        result["extracted"] = {}

    if page_content_type:
        if page_content_type == "rendered":
            result["page_content"] = await page.content()
        else:
            result["page_content"] = await page.content()

    return result
