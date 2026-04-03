"""Sync version of crawler for Windows (SelectorEventLoop) compatibility."""

from __future__ import annotations

import logging
from typing import Any

from shared.config.models import FieldExtractor, HostConfig, PreAction, SelectorItem
from shared.transform.pipeline import apply_transforms

logger = logging.getLogger(__name__)

STEALTH_JS = """
() => {
    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
    window.chrome = { runtime: {} };
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) =>
        parameters.name === 'notifications'
            ? Promise.resolve({ state: Notification.permission })
            : originalQuery(parameters);
    Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
    Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
}
"""


def _execute_pre_action(page, action: PreAction) -> None:  # noqa: ANN001
    match action.action_type:
        case "wait":
            page.wait_for_timeout(action.timeout or 1000)
        case "wait_for_selector":
            if action.selector:
                page.wait_for_selector(action.selector, timeout=action.timeout or 10000)
        case "click":
            if action.selector:
                page.click(action.selector)
        case "scroll":
            direction = action.direction or "down"
            pixels = action.pixels or 300
            delta = pixels if direction == "down" else -pixels
            page.evaluate(f"window.scrollBy(0, {delta})")
        case "input":
            if action.selector and action.text:
                page.fill(action.selector, action.text)


def _extract_field(page, extractor: FieldExtractor) -> Any:  # noqa: ANN001
    for selector_raw in extractor.selectors:
        try:
            if isinstance(selector_raw, dict):
                sel = SelectorItem(**selector_raw)
            elif isinstance(selector_raw, SelectorItem):
                sel = selector_raw
            else:
                sel = SelectorItem(value=str(selector_raw))

            if extractor.multiple:
                elements = page.query_selector_all(sel.value)
                if not elements:
                    continue
                values = []
                for el in elements:
                    v = el.get_attribute(sel.attribute) if sel.attribute else el.text_content()
                    if v is not None:
                        values.append(v)
                if values:
                    return values
            else:
                element = page.query_selector(sel.value)
                if element is None:
                    continue
                value = element.get_attribute(sel.attribute) if sel.attribute else element.text_content()
                if value is not None:
                    return value
        except Exception:
            logger.debug("Selector %s failed", selector_raw, exc_info=True)
            continue
    return None


def sync_navigate_and_extract(
    page,  # noqa: ANN001
    url: str,
    config: HostConfig | None,
    *,
    performance_mode: bool = False,
    page_content_type: str | None = None,
) -> dict[str, Any]:
    wait_until = "domcontentloaded" if performance_mode else (config.wait_until if config else "networkidle")

    page.add_init_script(STEALTH_JS)
    page.goto(url, wait_until=wait_until, timeout=30000)

    result: dict[str, Any] = {"url": url, "status": "ok"}

    if config:
        for action in config.pre_actions:
            _execute_pre_action(page, action)

        extracted: dict[str, Any] = {}
        for field_name, extractor in config.field_extractors.items():
            value = _extract_field(page, extractor)
            if value is None and extractor.required:
                logger.warning("Required field %s not found", field_name)
                extracted[field_name] = None
                continue
            if value is not None and extractor.transforms:
                value = apply_transforms(value, extractor.transforms)
            extracted[field_name] = value
        result["extracted"] = extracted
    else:
        result["extracted"] = {}

    if page_content_type:
        result["page_content"] = page.content()

    return result
