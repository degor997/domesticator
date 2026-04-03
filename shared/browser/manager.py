from __future__ import annotations

import asyncio
import logging
import sys
import traceback

from playwright.async_api import Browser, Playwright, async_playwright

from shared.browser.bypass.stealth import get_random_user_agent, get_random_viewport

logger = logging.getLogger(__name__)


def _ensure_proactor_on_windows() -> None:
    """Windows requires ProactorEventLoop for subprocess support in asyncio."""
    if sys.platform != "win32":
        return
    loop = asyncio.get_event_loop()
    if not isinstance(loop, asyncio.ProactorEventLoop):
        logger.info("Switching to ProactorEventLoop for Windows subprocess support")
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)


class BrowserManager:
    def __init__(self) -> None:
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self.start_error: str | None = None

    async def start(self) -> None:
        try:
            _ensure_proactor_on_windows()
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                ],
            )
            self.start_error = None
            logger.info("Browser started")
        except Exception as exc:
            tb = traceback.format_exc()
            self.start_error = f"{type(exc).__name__}: {exc}\n{tb}"
            logger.error("Browser failed to start:\n%s", tb)

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
            err = self.start_error or "unknown reason"
            raise RuntimeError(f"Browser not available ({err}). Run: playwright install chromium --with-deps")

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
