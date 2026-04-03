from __future__ import annotations


def text_contains(value: str | None, *, search: str) -> bool | None:
    if value is None:
        return None
    return search in str(value)


def toggle_boolean(value: bool | None) -> bool | None:
    if value is None:
        return None
    return not bool(value)


def true_to_text(value: bool | None, *, new: str) -> str | None:
    if value is None:
        return None
    if bool(value):
        return new
    return None
