from __future__ import annotations

import logging
import random

from fake_useragent import UserAgent

logger = logging.getLogger(__name__)

_ua = UserAgent(browsers=["chrome", "edge"])

STEALTH_JS = """
() => {
    // Overwrite navigator.webdriver
    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});

    // Overwrite chrome runtime
    window.chrome = { runtime: {} };

    // Overwrite permissions
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) =>
        parameters.name === 'notifications'
            ? Promise.resolve({ state: Notification.permission })
            : originalQuery(parameters);

    // Overwrite plugins
    Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5],
    });

    // Overwrite languages
    Object.defineProperty(navigator, 'languages', {
        get: () => ['en-US', 'en'],
    });
}
"""

VIEWPORT_SIZES = [
    {"width": 1920, "height": 1080},
    {"width": 1366, "height": 768},
    {"width": 1536, "height": 864},
    {"width": 1440, "height": 900},
    {"width": 1280, "height": 720},
]


def get_random_user_agent() -> str:
    return _ua.random


def get_random_viewport() -> dict[str, int]:
    return random.choice(VIEWPORT_SIZES)


async def apply_stealth(page) -> None:  # noqa: ANN001
    await page.add_init_script(STEALTH_JS)
    logger.debug("Applied stealth scripts to page")
