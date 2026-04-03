from __future__ import annotations

import itertools
import logging
import threading

logger = logging.getLogger(__name__)


class ProxyManager:
    def __init__(self) -> None:
        self._proxies: list[str] = []
        self._cycle: itertools.cycle[str] | None = None
        self._lock = threading.Lock()

    def add(self, proxy_url: str) -> bool:
        with self._lock:
            if proxy_url in self._proxies:
                return False
            self._proxies.append(proxy_url)
            self._cycle = itertools.cycle(self._proxies)
            logger.info("Added proxy: %s", proxy_url)
            return True

    def remove(self, proxy_url: str) -> bool:
        with self._lock:
            if proxy_url not in self._proxies:
                return False
            self._proxies.remove(proxy_url)
            self._cycle = itertools.cycle(self._proxies) if self._proxies else None
            logger.info("Removed proxy: %s", proxy_url)
            return True

    def get_next(self) -> str | None:
        with self._lock:
            if self._cycle is None:
                return None
            return next(self._cycle)

    def list_all(self) -> list[str]:
        with self._lock:
            return list(self._proxies)
