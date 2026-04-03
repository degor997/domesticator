from __future__ import annotations

import logging

from playwright.async_api import Browser, Playwright, async_playwright

from shared.browser.bypass.stealth import get_random_user_agent, get_random_viewport

logger = logging.getLogger(__name__)


class BrowserManager:
    def __init__(self) -> None:
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None

    async def start(self) -> None:
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )
        logger.info("Browser started")

    async def stop(self) -> None:
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
        logger.info("Browser stopped")

    async def new_context(self, *, proxy: str | None = None):  # noqa: ANN204
        if self._browser is None:
            raise RuntimeError("Browser not started")

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

        context = await self._browser.new_context(**ctx_kwargs)
        return context

    @property
    def is_running(self) -> bool:
        return self._browser is not None
