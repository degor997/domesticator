from __future__ import annotations

import json
import logging
from pathlib import Path

from shared.config.models import HostConfig
from shared.config.store import ConfigStore

logger = logging.getLogger(__name__)

HOSTS_JSON = Path(__file__).resolve().parent.parent.parent / "configs" / "hosts.json"


class MemoryConfigStore(ConfigStore):
    def __init__(self) -> None:
        self._data: dict[str, dict[str, HostConfig]] = {}

    async def load_from_file(self, path: Path = HOSTS_JSON) -> None:
        if not path.exists():
            logger.warning("hosts.json not found at %s", path)
            return
        raw = json.loads(path.read_text(encoding="utf-8"))
        for hostname, strategies in raw.items():
            self._data[hostname] = {}
            for strategy, cfg in strategies.items():
                self._data[hostname][strategy] = HostConfig(**cfg)
        logger.info("Loaded %d host configs from %s", len(self._data), path)

    async def get_all(self) -> dict[str, dict[str, HostConfig]]:
        return dict(self._data)

    async def get_host(self, hostname: str) -> dict[str, HostConfig] | None:
        return self._data.get(hostname)

    async def get_strategies(self, hostname: str) -> list[str]:
        host = self._data.get(hostname)
        if host is None:
            return []
        return list(host.keys())

    async def get_config(self, hostname: str, strategy: str) -> HostConfig | None:
        host = self._data.get(hostname)
        if host is None:
            return None
        return host.get(strategy)

    async def add_config(self, hostname: str, strategy: str, config: HostConfig) -> bool:
        if hostname in self._data and strategy in self._data[hostname]:
            return False
        if hostname not in self._data:
            self._data[hostname] = {}
        self._data[hostname][strategy] = config
        return True

    async def update_config(self, hostname: str, strategy: str, config: HostConfig) -> bool:
        if hostname not in self._data or strategy not in self._data[hostname]:
            return False
        self._data[hostname][strategy] = config
        return True

    async def delete_config(self, hostname: str, strategy: str | None = None) -> bool:
        if hostname not in self._data:
            return False
        if strategy is None:
            del self._data[hostname]
            return True
        if strategy not in self._data[hostname]:
            return False
        del self._data[hostname][strategy]
        if not self._data[hostname]:
            del self._data[hostname]
        return True
