from __future__ import annotations

import asyncio
import logging
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor

from playwright.async_api import Browser, Playwright, async_playwright
from playwright.sync_api import sync_playwright

from shared.browser.bypass.stealth import get_random_user_agent, get_random_viewport

logger = logging.getLogger(__name__)

_executor = ThreadPoolExecutor(max_workers=1)


def _check_subprocess_support() -> bool:
    """Check if current event loop supports subprocesses (needed for Playwright)."""
    if sys.platform != "win32":
        return True
    loop = asyncio.get_event_loop()
    return hasattr(loop, "_make_subprocess_transport") and type(loop).__name__ == "ProactorEventLoop"


def _sync_launch_playwright():
    """Launch Playwright synchronously in a thread — works on any event loop."""
    p = sync_playwright().start()
    b = p.chromium.launch(
        headless=True,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-dev-shm-usage",
        ],
    )
    return p, b


class BrowserManager:
    def __init__(self) -> None:
        self._playwright: Playwright | None = None
        self._sync_playwright = None
        self._browser: Browser | None = None
        self._sync_browser = None
        self.start_error: str | None = None
        self._use_sync: bool = False

    async def start(self) -> None:
        try:
            if _check_subprocess_support():
                # Async path (Linux/macOS or Windows with ProactorEventLoop)
                self._playwright = await async_playwright().start()
                self._browser = await self._playwright.chromium.launch(
                    headless=True,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                    ],
                )
            else:
                # Windows fallback: launch in thread with sync API
                logger.info("Using sync Playwright (Windows SelectorEventLoop detected)")
                loop = asyncio.get_event_loop()
                self._sync_playwright, self._sync_browser = await loop.run_in_executor(
                    _executor, _sync_launch_playwright
                )
                self._use_sync = True

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
        if self._sync_browser:
            self._sync_browser.close()
            self._sync_browser = None
        if self._sync_playwright:
            self._sync_playwright.stop()
            self._sync_playwright = None
        logger.info("Browser stopped")

    async def new_context(self, *, proxy: str | None = None):  # noqa: ANN204
        browser = self._browser or self._sync_browser
        if browser is None:
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

        if self._use_sync:
            loop = asyncio.get_event_loop()
            context = await loop.run_in_executor(_executor, lambda: browser.new_context(**ctx_kwargs))
        else:
            context = await browser.new_context(**ctx_kwargs)
        return context

    @property
    def is_running(self) -> bool:
        return self._browser is not None or self._sync_browser is not None
