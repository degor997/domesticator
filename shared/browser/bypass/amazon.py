from __future__ import annotations

import asyncio
import logging
import random

logger = logging.getLogger(__name__)

CAPTCHA_SELECTORS = [
    "#captchacharacters",
    "form[action*='validateCaptcha']",
    ".a-box-inner h4",
]

BOT_DETECTION_MARKERS = [
    "sorry, we just need to make sure you're not a robot",
    "enter the characters you see below",
    "type the characters you see in this image",
]


async def detect_amazon_block(page) -> bool:  # noqa: ANN001
    content = await page.content()
    content_lower = content.lower()
    for marker in BOT_DETECTION_MARKERS:
        if marker in content_lower:
            logger.info("Amazon bot detection triggered")
            return True

    for selector in CAPTCHA_SELECTORS:
        try:
            el = await page.query_selector(selector)
            if el:
                return True
        except Exception:
            continue

    return False


async def simulate_human_behavior(page) -> None:  # noqa: ANN001
    await asyncio.sleep(random.uniform(0.5, 1.5))

    # Random mouse movements
    for _ in range(random.randint(2, 5)):
        x = random.randint(100, 800)
        y = random.randint(100, 600)
        await page.mouse.move(x, y)
        await asyncio.sleep(random.uniform(0.1, 0.3))

    # Random scroll
    scroll_y = random.randint(100, 400)
    await page.evaluate(f"window.scrollBy(0, {scroll_y})")
    await asyncio.sleep(random.uniform(0.3, 0.8))


async def bypass_amazon(page, *, max_retries: int = 3) -> bool:  # noqa: ANN001
    for attempt in range(max_retries):
        if not await detect_amazon_block(page):
            return True

        logger.info("Amazon bypass attempt %d/%d", attempt + 1, max_retries)
        await simulate_human_behavior(page)
        await asyncio.sleep(random.uniform(1.0, 3.0))

    blocked = await detect_amazon_block(page)
    if blocked:
        logger.warning("Amazon bypass failed after %d attempts", max_retries)
    return not blocked
