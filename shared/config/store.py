from __future__ import annotations

import abc

from shared.config.models import HostConfig


class ConfigStore(abc.ABC):
    @abc.abstractmethod
    async def get_all(self) -> dict[str, dict[str, HostConfig]]:
        ...

    @abc.abstractmethod
    async def get_host(self, hostname: str) -> dict[str, HostConfig] | None:
        ...

    @abc.abstractmethod
    async def get_strategies(self, hostname: str) -> list[str]:
        ...

    @abc.abstractmethod
    async def get_config(self, hostname: str, strategy: str) -> HostConfig | None:
        ...

    @abc.abstractmethod
    async def add_config(self, hostname: str, strategy: str, config: HostConfig) -> bool:
        ...

    @abc.abstractmethod
    async def update_config(self, hostname: str, strategy: str, config: HostConfig) -> bool:
        ...

    @abc.abstractmethod
    async def delete_config(self, hostname: str, strategy: str | None = None) -> bool:
        ...
