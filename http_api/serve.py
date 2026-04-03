"""Entrypoint that ensures correct event loop policy on Windows before uvicorn starts."""

from __future__ import annotations

import asyncio
import sys


def main() -> None:
    # Windows needs ProactorEventLoop for subprocess support (Playwright)
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    import uvicorn

    uvicorn.run(
        "http_api.run:server",
        host="0.0.0.0",
        port=8000,
        reload=True,
        loop="asyncio",
    )


if __name__ == "__main__":
    main()
