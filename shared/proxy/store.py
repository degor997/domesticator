from __future__ import annotations

import abc


class ProxyStore(abc.ABC):
    @abc.abstractmethod
    async def get_all(self) -> list[str]:
        ...

    @abc.abstractmethod
    async def add(self, proxy_url: str) -> bool:
        ...

    @abc.abstractmethod
    async def remove(self, proxy_url: str) -> bool:
        ...
