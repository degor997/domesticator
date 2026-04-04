from __future__ import annotations

import logging

from shared.proxy.store import ProxyStore

logger = logging.getLogger(__name__)


class MemoryProxyStore(ProxyStore):
    def __init__(self) -> None:
        self._proxies: list[str] = []

    async def get_all(self) -> list[str]:
        return list(self._proxies)

    async def add(self, proxy_url: str) -> bool:
        if proxy_url in self._proxies:
            return False
        self._proxies.append(proxy_url)
        return True

    async def remove(self, proxy_url: str) -> bool:
        if proxy_url not in self._proxies:
            return False
        self._proxies.remove(proxy_url)
        return True
