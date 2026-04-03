from __future__ import annotations

import unicodedata


def clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = unicodedata.normalize("NFKC", str(value))
    text = " ".join(text.split())
    return text.strip()


def strip_whitespace(value: str | None) -> str | None:
    if value is None:
        return None
    return str(value).strip()


def to_lower(value: str | None) -> str | None:
    if value is None:
        return None
    return str(value).lower()


def to_upper(value: str | None) -> str | None:
    if value is None:
        return None
    return str(value).upper()


def to_text(value: object) -> str | None:
    if value is None:
        return None
    return str(value)
