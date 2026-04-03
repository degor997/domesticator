"""Tests for all transform functions."""


from shared.transform.transformers.array import first, join_with, last, pick
from shared.transform.transformers.logic import text_contains, toggle_boolean, true_to_text
from shared.transform.transformers.price import extract_numbers, text_to_price
from shared.transform.transformers.string_ops import regex_extract, regex_replace, replace_text, split_by, substring
from shared.transform.transformers.text import clean_text, strip_whitespace, to_lower, to_text, to_upper

# --- Text transforms ---

class TestCleanText:
    def test_basic(self):
        assert clean_text("  hello   world  ") == "hello world"

    def test_unicode_normalization(self):
        assert clean_text("\u00a0text\u00a0") == "text"

    def test_none(self):
        assert clean_text(None) is None

    def test_multiline(self):
        assert clean_text("line1\n  line2\t line3") == "line1 line2 line3"


class TestStripWhitespace:
    def test_basic(self):
        assert strip_whitespace("  hello  ") == "hello"

    def test_none(self):
        assert strip_whitespace(None) is None


class TestToLower:
    def test_basic(self):
        assert to_lower("HELLO") == "hello"

    def test_none(self):
        assert to_lower(None) is None


class TestToUpper:
    def test_basic(self):
        assert to_upper("hello") == "HELLO"

    def test_none(self):
        assert to_upper(None) is None


class TestToText:
    def test_int(self):
        assert to_text(42) == "42"

    def test_none(self):
        assert to_text(None) is None


# --- Price transforms ---

class TestTextToPrice:
    def test_rubles(self):
        assert text_to_price("₽ 1 234,56") == 123456

    def test_dollars(self):
        assert text_to_price("$12,345.67 USD") == 1234567

    def test_euros(self):
        assert text_to_price("€1.234,50") == 123450

    def test_lira(self):
        assert text_to_price("₺ 2.999,95 TL") == 299995

    def test_simple(self):
        assert text_to_price("100") == 10000

    def test_none(self):
        assert text_to_price(None) is None

    def test_empty(self):
        assert text_to_price("") is None

    def test_just_currency(self):
        assert text_to_price("$") is None


class TestExtractNumbers:
    def test_basic(self):
        assert extract_numbers("abc123def456") == "123456"

    def test_none(self):
        assert extract_numbers(None) is None

    def test_no_numbers(self):
        assert extract_numbers("abc") is None


# --- String ops ---

class TestRegexExtract:
    def test_basic(self):
        assert regex_extract("price: 123.45", pattern=r"(\d+\.\d+)", group=1) == "123.45"

    def test_no_match(self):
        assert regex_extract("no numbers", pattern=r"\d+") is None

    def test_none(self):
        assert regex_extract(None, pattern=r"\d+") is None


class TestRegexReplace:
    def test_basic(self):
        assert regex_replace("hello 123 world", pattern=r"\d+", replacement="NUM") == "hello NUM world"

    def test_none(self):
        assert regex_replace(None, pattern=r"\d+") is None


class TestReplaceText:
    def test_basic(self):
        assert replace_text("hello world", old="world", new="earth") == "hello earth"

    def test_none(self):
        assert replace_text(None, old="a", new="b") is None


class TestSubstring:
    def test_basic(self):
        assert substring("hello world", start=6) == "world"

    def test_with_end(self):
        assert substring("hello world", start=0, end=5) == "hello"

    def test_none(self):
        assert substring(None, start=0) is None


class TestSplitBy:
    def test_basic(self):
        assert split_by("a,b,c", separator=",") == ["a", "b", "c"]

    def test_none(self):
        assert split_by(None, separator=",") is None


# --- Array transforms ---

class TestFirst:
    def test_basic(self):
        assert first([1, 2, 3]) == 1

    def test_empty(self):
        assert first([]) is None

    def test_not_list(self):
        assert first("hello") == "hello"


class TestLast:
    def test_basic(self):
        assert last([1, 2, 3]) == 3

    def test_empty(self):
        assert last([]) is None


class TestPick:
    def test_basic(self):
        assert pick([10, 20, 30], index=1) == 20

    def test_out_of_range(self):
        assert pick([1, 2], index=5) is None


class TestJoinWith:
    def test_basic(self):
        assert join_with(["a", "b", "c"], separator="-") == "a-b-c"

    def test_none(self):
        assert join_with(None, separator=",") is None


# --- Logic transforms ---

class TestTextContains:
    def test_found(self):
        assert text_contains("hello world", search="world") is True

    def test_not_found(self):
        assert text_contains("hello", search="world") is False

    def test_none(self):
        assert text_contains(None, search="x") is None


class TestToggleBoolean:
    def test_true(self):
        assert toggle_boolean(True) is False

    def test_false(self):
        assert toggle_boolean(False) is True

    def test_none(self):
        assert toggle_boolean(None) is None


class TestTrueToText:
    def test_true(self):
        assert true_to_text(True, new="YES") == "YES"

    def test_false(self):
        assert true_to_text(False, new="YES") is None

    def test_none(self):
        assert true_to_text(None, new="YES") is None
