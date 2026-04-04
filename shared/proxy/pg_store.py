from __future__ import annotations

import logging

import asyncpg

from shared.proxy.store import ProxyStore

logger = logging.getLogger(__name__)

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS proxies (
    proxy_url TEXT PRIMARY KEY
);
"""


class PgProxyStore(ProxyStore):
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def init_schema(self) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute(CREATE_TABLE)

    async def seed_if_empty(self, proxy_list: str) -> None:
        if not proxy_list:
            return
        async with self._pool.acquire() as conn:
            count = await conn.fetchval("SELECT count(*) FROM proxies")
            if count > 0:
                return
            for proxy in proxy_list.split(","):
                proxy = proxy.strip()
                if proxy:
                    await conn.execute(
                        "INSERT INTO proxies (proxy_url) VALUES ($1) ON CONFLICT DO NOTHING",
                        proxy,
                    )
        logger.info("Seeded proxies from PROXY_LIST")

    async def get_all(self) -> list[str]:
        async with self._pool.acquire() as conn:
            rows = await conn.fetch("SELECT proxy_url FROM proxies")
        return [row["proxy_url"] for row in rows]

    async def add(self, proxy_url: str) -> bool:
        try:
            async with self._pool.acquire() as conn:
                await conn.execute(
                    "INSERT INTO proxies (proxy_url) VALUES ($1)",
                    proxy_url,
                )
            return True
        except asyncpg.UniqueViolationError:
            return False

    async def remove(self, proxy_url: str) -> bool:
        async with self._pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM proxies WHERE proxy_url = $1",
                proxy_url,
            )
        count = int(result.split()[-1])
        return count > 0
