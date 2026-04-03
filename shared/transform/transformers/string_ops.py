from __future__ import annotations

import re


def regex_extract(value: str | None, *, pattern: str, group: int = 0) -> str | None:
    if value is None:
        return None
    match = re.search(pattern, str(value))
    if match is None:
        return None
    try:
        return match.group(group)
    except IndexError:
        return match.group(0)


def regex_replace(value: str | None, *, pattern: str, replacement: str = "") -> str | None:
    if value is None:
        return None
    return re.sub(pattern, replacement, str(value))


def replace_text(value: str | None, *, old: str, new: str) -> str | None:
    if value is None:
        return None
    return str(value).replace(old, new)


def substring(value: str | None, *, start: int = 0, end: int | None = None) -> str | None:
    if value is None:
        return None
    return str(value)[start:end]


def split_by(value: str | None, *, separator: str = ",", maxsplit: int = -1) -> list[str] | None:
    if value is None:
        return None
    return str(value).split(separator, maxsplit)
