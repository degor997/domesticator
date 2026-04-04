from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from http_api.routers import register_routers
from shared.browser.manager import BrowserManager
from shared.config.memory_store import MemoryConfigStore
from shared.proxy.manager import ProxyManager
from shared.proxy.memory_store import MemoryProxyStore
from shared.utils.logging import setup_logging

logger = logging.getLogger(__name__)


async def _create_config_store():
    app_env = os.getenv("APP_ENV", "development").lower()
    pg_conn = os.getenv("PG_CONNECTION")

    if app_env in ("production", "prod"):
        if not pg_conn:
            raise RuntimeError("PG_CONNECTION is required in production mode")
        return await _create_pg_store(pg_conn)

    # Development
    if pg_conn:
        return await _create_pg_store(pg_conn)

    # In-memory fallback
    store = MemoryConfigStore()
    await store.load_from_file()
    logger.info("Using in-memory config store")
    return store


async def _create_pg_store(pg_conn: str):
    import asyncpg

    from shared.config.pg_store import PgConfigStore

    pool = await asyncpg.create_pool(pg_conn)
    store = PgConfigStore(pool)
    await store.init_schema()
    await store.seed_if_empty()
    logger.info("Using PostgreSQL config store")
    return store


async def _create_proxy_store(pg_pool=None):
    proxy_list = os.getenv("PROXY_LIST", "")

    if pg_pool is not None:
        from shared.proxy.pg_store import PgProxyStore

        store = PgProxyStore(pg_pool)
        await store.init_schema()
        await store.seed_if_empty(proxy_list)
        logger.info("Using PostgreSQL proxy store")
        return store

    store = MemoryProxyStore()
    for proxy in proxy_list.split(","):
        proxy = proxy.strip()
        if proxy:
            await store.add(proxy)
    logger.info("Using in-memory proxy store")
    return store


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Starting Domesticator...")

    app.state.config_store = await _create_config_store()

    # Extract pg pool if available for proxy store
    pg_pool = getattr(app.state.config_store, "_pool", None)
    proxy_store = await _create_proxy_store(pg_pool)

    app.state.proxy_manager = ProxyManager(proxy_store)
    await app.state.proxy_manager.reload()

    app.state.browser_manager = BrowserManager()
    await app.state.browser_manager.start()

    logger.info("Domesticator started")
    yield

    if app.state.browser_manager.is_running:
        await app.state.browser_manager.stop()
    logger.info("Domesticator stopped")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Domesticator",
        description="Web scraping service with configurable selectors and data transformation",
        version="1.0.0",
        lifespan=lifespan,
    )
    register_routers(app)
    return app


server = create_app()
