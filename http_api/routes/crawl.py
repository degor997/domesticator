from __future__ import annotations

import logging
import time

from fastapi import APIRouter, Request

from shared.browser.crawl import crawl_targets
from shared.config.models import CrawlRequest, CrawlResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v0")


@router.post("/crawl", response_model=CrawlResponse)
async def crawl(body: CrawlRequest, request: Request):
    browser_manager = request.app.state.browser_manager
    config_store = request.app.state.config_store
    proxy_manager = request.app.state.proxy_manager

    start = time.monotonic()
    results = await crawl_targets(
        body.targets,
        browser_manager,
        config_store,
        proxy_manager,
    )
    elapsed = time.monotonic() - start
    logger.info("Crawled %d targets in %.2fs", len(body.targets), elapsed)

    return CrawlResponse(results=results)
