from __future__ import annotations

from typing import Any, Callable

from shared.transform.transformers.array import first, join_with, last, pick
from shared.transform.transformers.logic import text_contains, toggle_boolean, true_to_text
from shared.transform.transformers.price import extract_numbers, text_to_price
from shared.transform.transformers.string_ops import regex_extract, regex_replace, replace_text, split_by, substring
from shared.transform.transformers.text import clean_text, strip_whitespace, to_lower, to_text, to_upper

TRANSFORM_REGISTRY: dict[str, Callable[..., Any]] = {
    "clean_text": clean_text,
    "strip_whitespace": strip_whitespace,
    "to_lower": to_lower,
    "to_upper": to_upper,
    "to_text": to_text,
    "text_to_price": text_to_price,
    "extract_numbers": extract_numbers,
    "regex_extract": regex_extract,
    "regex_replace": regex_replace,
    "replace_text": replace_text,
    "substring": substring,
    "split_by": split_by,
    "first": first,
    "last": last,
    "pick": pick,
    "join_with": join_with,
    "text_contains": text_contains,
    "toggle_boolean": toggle_boolean,
    "true_to_text": true_to_text,
}
