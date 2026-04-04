from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from http_api.routers import register_routers
from shared.browser.manager import BrowserManager
from shared.config.memory_store import MemoryConfigStore
from shared.proxy.manager import ProxyManager
from shared.proxy.memory_store import MemoryProxyStore


@pytest.fixture
def proxy_manager():
    return ProxyManager(MemoryProxyStore())


@pytest.fixture
async def config_store():
    store = MemoryConfigStore()
    await store.load_from_file()
    return store


@pytest.fixture
def browser_manager():
    bm = MagicMock(spec=BrowserManager)
    bm.is_running = True
    bm.start_error = None
    bm.start = AsyncMock()
    bm.stop = AsyncMock()
    bm.new_context = AsyncMock()
    return bm


@pytest.fixture
async def app(config_store, proxy_manager, browser_manager):
    app = FastAPI()
    app.state.config_store = config_store
    app.state.proxy_manager = proxy_manager
    app.state.browser_manager = browser_manager
    register_routers(app)
    return app


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
