from __future__ import annotations

import json
import logging
from pathlib import Path

import asyncpg

from shared.config.models import HostConfig
from shared.config.store import ConfigStore

logger = logging.getLogger(__name__)

HOSTS_JSON = Path(__file__).resolve().parent.parent.parent / "configs" / "hosts.json"

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS host_configs (
    hostname TEXT NOT NULL,
    strategy TEXT NOT NULL,
    config JSONB NOT NULL,
    PRIMARY KEY (hostname, strategy)
);
"""


class PgConfigStore(ConfigStore):
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def init_schema(self) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute(CREATE_TABLE)

    async def seed_if_empty(self, path: Path = HOSTS_JSON) -> None:
        async with self._pool.acquire() as conn:
            count = await conn.fetchval("SELECT count(*) FROM host_configs")
            if count > 0:
                return
        if not path.exists():
            logger.warning("hosts.json not found at %s, skipping seed", path)
            return
        raw = json.loads(path.read_text(encoding="utf-8"))
        async with self._pool.acquire() as conn:
            for hostname, strategies in raw.items():
                for strategy, cfg in strategies.items():
                    sql = (
                        "INSERT INTO host_configs (hostname, strategy, config)"
                        " VALUES ($1, $2, $3) ON CONFLICT DO NOTHING"
                    )
                    await conn.execute(
                        sql,
                        hostname,
                        strategy,
                        json.dumps(cfg),
                    )
        logger.info("Seeded host configs from %s", path)

    async def get_all(self) -> dict[str, dict[str, HostConfig]]:
        async with self._pool.acquire() as conn:
            rows = await conn.fetch("SELECT hostname, strategy, config FROM host_configs")
        result: dict[str, dict[str, HostConfig]] = {}
        for row in rows:
            hostname = row["hostname"]
            if hostname not in result:
                result[hostname] = {}
            result[hostname][row["strategy"]] = HostConfig(**json.loads(row["config"]))
        return result

    async def get_host(self, hostname: str) -> dict[str, HostConfig] | None:
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT strategy, config FROM host_configs WHERE hostname = $1", hostname
            )
        if not rows:
            return None
        return {row["strategy"]: HostConfig(**json.loads(row["config"])) for row in rows}

    async def get_strategies(self, hostname: str) -> list[str]:
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT strategy FROM host_configs WHERE hostname = $1", hostname
            )
        return [row["strategy"] for row in rows]

    async def get_config(self, hostname: str, strategy: str) -> HostConfig | None:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT config FROM host_configs WHERE hostname = $1 AND strategy = $2",
                hostname,
                strategy,
            )
        if row is None:
            return None
        return HostConfig(**json.loads(row["config"]))

    async def add_config(self, hostname: str, strategy: str, config: HostConfig) -> bool:
        try:
            async with self._pool.acquire() as conn:
                await conn.execute(
                    "INSERT INTO host_configs (hostname, strategy, config) VALUES ($1, $2, $3)",
                    hostname,
                    strategy,
                    config.model_dump_json(),
                )
            return True
        except asyncpg.UniqueViolationError:
            return False

    async def update_config(self, hostname: str, strategy: str, config: HostConfig) -> bool:
        async with self._pool.acquire() as conn:
            result = await conn.execute(
                "UPDATE host_configs SET config = $3 WHERE hostname = $1 AND strategy = $2",
                hostname,
                strategy,
                config.model_dump_json(),
            )
        return result == "UPDATE 1"

    async def delete_config(self, hostname: str, strategy: str | None = None) -> bool:
        async with self._pool.acquire() as conn:
            if strategy is None:
                result = await conn.execute(
                    "DELETE FROM host_configs WHERE hostname = $1", hostname
                )
            else:
                result = await conn.execute(
                    "DELETE FROM host_configs WHERE hostname = $1 AND strategy = $2",
                    hostname,
                    strategy,
                )
        count = int(result.split()[-1])
        return count > 0
