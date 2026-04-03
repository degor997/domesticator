from __future__ import annotations

import asyncio
import logging

logger = logging.getLogger(__name__)

CF_CHALLENGE_SELECTORS = [
    "#challenge-running",
    "#challenge-stage",
    ".cf-browser-verification",
    "#cf-challenge-running",
]

CF_TITLE_MARKERS = [
    "just a moment",
    "checking your browser",
    "attention required",
]


async def detect_cloudflare(page) -> bool:  # noqa: ANN001
    title = (await page.title()).lower()
    for marker in CF_TITLE_MARKERS:
        if marker in title:
            logger.info("Cloudflare challenge detected via title")
            return True

    for selector in CF_CHALLENGE_SELECTORS:
        try:
            el = await page.query_selector(selector)
            if el:
                logger.info("Cloudflare challenge detected via selector: %s", selector)
                return True
        except Exception:
            continue

    return False


async def bypass_cloudflare(page, *, max_wait: int = 15000) -> bool:  # noqa: ANN001
    if not await detect_cloudflare(page):
        return True

    logger.info("Attempting Cloudflare bypass, waiting up to %dms", max_wait)
    elapsed = 0
    step = 1000

    while elapsed < max_wait:
        await asyncio.sleep(step / 1000)
        elapsed += step

        if not await detect_cloudflare(page):
            logger.info("Cloudflare challenge passed after %dms", elapsed)
            return True

    logger.warning("Cloudflare bypass timed out after %dms", max_wait)
    return False
