from __future__ import annotations

import enum
from typing import Any

from pydantic import BaseModel, Field


class HostStatus(str, enum.Enum):
    ACTIVE = "active"
    DRAFT = "draft"
    DISABLED = "disabled"


class SelectorItem(BaseModel):
    value: str
    attribute: str | None = None


Selector = str | SelectorItem


class FieldExtractor(BaseModel):
    selectors: list[Selector]
    required: bool = False
    multiple: bool = False
    transforms: list[str | dict[str, Any]] = Field(default_factory=list)


class PreAction(BaseModel):
    action_type: str
    selector: str | None = None
    timeout: int | None = None
    direction: str | None = None
    pixels: int | None = None
    text: str | None = None


class HostConfig(BaseModel):
    field_extractors: dict[str, FieldExtractor] = Field(default_factory=dict)
    pre_actions: list[PreAction] = Field(default_factory=list)
    wait_until: str = "networkidle"
    performance_mode: bool = False
    status: HostStatus = HostStatus.ACTIVE
    frozen: bool = False


class PageContentType(str, enum.Enum):
    UNRENDERED = "unrendered"
    RENDERED = "rendered"


class PageContentRequest(BaseModel):
    type: PageContentType = PageContentType.UNRENDERED


class CrawlTarget(BaseModel):
    url: str
    with_page_content: PageContentRequest | None = None
    require_host_config: bool = True
    performance_mode: bool | None = None
    strategy: str = "default"


class CrawlRequest(BaseModel):
    targets: list[CrawlTarget]


class CrawlResultItem(BaseModel):
    url: str
    status: str = "ok"
    extracted: dict[str, Any] = Field(default_factory=dict)
    page_content: str | None = None
    error: str | None = None


class CrawlResponse(BaseModel):
    results: list[CrawlResultItem]


class ProxyAddRequest(BaseModel):
    proxy_url: str
