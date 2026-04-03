from __future__ import annotations

from typing import Any


def first(value: list | None) -> Any:
    if value is None or not isinstance(value, list):
        return value
    return value[0] if value else None


def last(value: list | None) -> Any:
    if value is None or not isinstance(value, list):
        return value
    return value[-1] if value else None


def pick(value: list | None, *, index: int = 0) -> Any:
    if not value or not isinstance(value, list):
        return value
    if index < 0 or index >= len(value):
        return None
    return value[index]


def join_with(value: list | None, *, separator: str = ",") -> str | None:
    if value is None:
        return None
    if not isinstance(value, list):
        return str(value)
    return separator.join(str(v) for v in value)
