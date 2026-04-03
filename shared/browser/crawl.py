from __future__ import annotations

import asyncio
import logging
from urllib.parse import urlparse

from shared.browser.crawler import navigate_and_extract
from shared.browser.manager import BrowserManager
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

        proxy = proxy_manager.get_next()
        context = await browser_manager.new_context(proxy=proxy)

        try:
            page = await context.new_page()
            page_content_type = target.with_page_content.type.value if target.with_page_content else None

            result = await navigate_and_extract(
                page,
                target.url,
                config,
                performance_mode=performance_mode,
                page_content_type=page_content_type,
            )

            return CrawlResultItem(
                url=result["url"],
                status=result["status"],
                extracted=result.get("extracted", {}),
                page_content=result.get("page_content"),
            )
        finally:
            await context.close()

    except Exception as exc:
        logger.exception("Crawl failed for %s", target.url)
        return CrawlResultItem(url=target.url, status="error", error=str(exc))


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
