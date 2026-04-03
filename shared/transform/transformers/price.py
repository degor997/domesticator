from __future__ import annotations

import re

_CURRENCY_SYMBOLS = re.compile(r"[₽$€£¥₴₸₺₩¢₫₣₤₦₧₨₪₭₮₯₰₱₲₳₵₶₷₹₺₻₼₽₾₿]")
_CURRENCY_CODES = re.compile(r"\b(USD|EUR|GBP|TRY|TL|RUB|UAH|KZT|JPY|KRW|CNY|INR)\b", re.IGNORECASE)


def text_to_price(value: str | None) -> int | None:
    """Convert price text to integer cents/kopecks (multiply by 100)."""
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None

    # Remove currency symbols and codes
    text = _CURRENCY_SYMBOLS.sub("", text)
    text = _CURRENCY_CODES.sub("", text)
    text = text.strip()

    if not text:
        return None

    # Determine decimal separator
    # Find last occurrence of . and ,
    last_dot = text.rfind(".")
    last_comma = text.rfind(",")

    if last_dot > last_comma:
        # Dot is decimal separator: 1,234.56 or 1234.56
        text = text.replace(",", "").replace(" ", "").replace("\u00a0", "")
        parts = text.split(".")
        if len(parts) == 2:
            integer_part = parts[0] or "0"
            decimal_part = parts[1][:2].ljust(2, "0")
        else:
            integer_part = text
            decimal_part = "00"
    elif last_comma > last_dot:
        # Comma is decimal separator: 1.234,56 or 1234,56
        text = text.replace(".", "").replace(" ", "").replace("\u00a0", "")
        parts = text.split(",")
        if len(parts) == 2:
            integer_part = parts[0] or "0"
            decimal_part = parts[1][:2].ljust(2, "0")
        else:
            integer_part = text
            decimal_part = "00"
    else:
        # No decimal separator
        text = text.replace(" ", "").replace("\u00a0", "")
        integer_part = text
        decimal_part = "00"

    # Clean non-digit chars
    integer_part = re.sub(r"[^\d]", "", integer_part)
    decimal_part = re.sub(r"[^\d]", "", decimal_part)[:2].ljust(2, "0")

    if not integer_part:
        integer_part = "0"

    return int(integer_part) * 100 + int(decimal_part)


def extract_numbers(value: str | None) -> str | None:
    """Extract only digits from text."""
    if value is None:
        return None
    result = re.sub(r"[^\d]", "", str(value))
    return result if result else None
