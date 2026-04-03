from __future__ import annotations

import asyncio
import logging
from typing import Any
from urllib.parse import urlparse

from shared.browser.crawler import navigate_and_extract
from shared.browser.manager import BrowserManager, _executor
from shared.browser.sync_crawler import sync_navigate_and_extract
from shared.config.models import CrawlResultItem, CrawlTarget, HostConfig
from shared.config.store import ConfigStore
from shared.proxy.manager import ProxyManager

logger = logging.getLogger(__name__)


async def _crawl_single(
    target: CrawlTarget,
    browser_manager: BrowserManager,
    config_store: ConfigStore,
    proxy_manager: ProxyManager,
) -> CrawlResultItem:
    try:
        raw_hostname = urlparse(target.url).hostname or ""
        hostname = raw_hostname.removeprefix("www.")

        # Resolve config
        config: HostConfig | None = None
        if target.require_host_config:
            config = await config_store.get_config(hostname, target.strategy)
            if config is None and hostname != raw_hostname:
                config = await config_store.get_config(raw_hostname, target.strategy)
            if config is None:
                return CrawlResultItem(url=target.url, status="error", error="host_config_not_found")
            if config.status != "active":
                return CrawlResultItem(url=target.url, status="error", error="host_config_inactive")

        performance_mode = target.performance_mode if target.performance_mode is not None else (
            config.performance_mode if config else False
        )
        page_content_type = target.with_page_content.type.value if target.with_page_content else None
        proxy = proxy_manager.get_next()

        if browser_manager._use_sync:
            # Windows sync path — run everything in a thread
            result = await _crawl_sync_in_thread(
                browser_manager, target.url, config, proxy,
                performance_mode=performance_mode,
                page_content_type=page_content_type,
            )
        else:
            # Normal async path
            context = await browser_manager.new_context(proxy=proxy)
            try:
                page = await context.new_page()
                result = await navigate_and_extract(
                    page, target.url, config,
                    performance_mode=performance_mode,
                    page_content_type=page_content_type,
                )
            finally:
                await context.close()

        return CrawlResultItem(
            url=result["url"],
            status=result["status"],
            extracted=result.get("extracted", {}),
            page_content=result.get("page_content"),
        )

    except Exception as exc:
        logger.exception("Crawl failed for %s", target.url)
        return CrawlResultItem(url=target.url, status="error", error=str(exc))


async def _crawl_sync_in_thread(
    browser_manager: BrowserManager,
    url: str,
    config: HostConfig | None,
    proxy: str | None,
    *,
    performance_mode: bool = False,
    page_content_type: str | None = None,
) -> dict[str, Any]:
    from shared.browser.bypass.stealth import get_random_user_agent, get_random_viewport

    def _run() -> dict[str, Any]:
        browser = browser_manager._sync_browser
        viewport = get_random_viewport()
        user_agent = get_random_user_agent()

        ctx_kwargs: dict = {
            "viewport": viewport,
            "user_agent": user_agent,
            "locale": "en-US",
            "timezone_id": "Europe/Istanbul",
        }
        if proxy:
            ctx_kwargs["proxy"] = {"server": proxy}

        context = browser.new_context(**ctx_kwargs)
        try:
            page = context.new_page()
            return sync_navigate_and_extract(
                page, url, config,
                performance_mode=performance_mode,
                page_content_type=page_content_type,
            )
        finally:
            context.close()

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _run)


async def crawl_targets(
    targets: list[CrawlTarget],
    browser_manager: BrowserManager,
    config_store: ConfigStore,
    proxy_manager: ProxyManager,
) -> list[CrawlResultItem]:
    tasks = [
        _crawl_single(target, browser_manager, config_store, proxy_manager)
        for target in targets
    ]
    results = await asyncio.gather(*tasks)
    return list(results)
