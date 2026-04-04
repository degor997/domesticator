from __future__ import annotations

import itertools
import logging
import threading

from shared.proxy.store import ProxyStore

logger = logging.getLogger(__name__)


class ProxyManager:
    def __init__(self, store: ProxyStore) -> None:
        self._store = store
        self._proxies: list[str] = []
        self._cycle: itertools.cycle[str] | None = None
        self._lock = threading.Lock()

    async def reload(self) -> None:
        proxies = await self._store.get_all()
        with self._lock:
            self._proxies = proxies
            self._cycle = itertools.cycle(self._proxies) if self._proxies else None

    async def add(self, proxy_url: str) -> bool:
        ok = await self._store.add(proxy_url)
        if ok:
            await self.reload()
            logger.info("Added proxy: %s", proxy_url)
        return ok

    async def remove(self, proxy_url: str) -> bool:
        ok = await self._store.remove(proxy_url)
        if ok:
            await self.reload()
            logger.info("Removed proxy: %s", proxy_url)
        return ok

    def get_next(self) -> str | None:
        with self._lock:
            if self._cycle is None:
                return None
            return next(self._cycle)

    async def list_all(self) -> list[str]:
        return await self._store.get_all()
