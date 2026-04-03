"""Tests for transform pipeline."""

from shared.transform.pipeline import apply_transforms


class TestApplyTransforms:
    def test_single_transform(self):
        assert apply_transforms("  hello  ", ["strip_whitespace"]) == "hello"

    def test_chain(self):
        assert apply_transforms("  HELLO  ", ["clean_text", "to_lower"]) == "hello"

    def test_price_pipeline(self):
        result = apply_transforms("₽ 1 234,56", ["clean_text", "text_to_price"])
        assert result == 123456

    def test_parametric_transform(self):
        result = apply_transforms("hello world", [{"name": "text_contains", "search": "world"}])
        assert result is True

    def test_unknown_transform(self):
        result = apply_transforms("hello", ["nonexistent_transform"])
        assert result == "hello"

    def test_complex_chain(self):
        result = apply_transforms(
            "  Price: 99.99 TL  ",
            [
                "clean_text",
                "to_lower",
                {"name": "text_contains", "search": "tl"},
                {"name": "true_to_text", "new": "TRY"},
            ],
        )
        assert result == "TRY"

    def test_empty_transforms(self):
        assert apply_transforms("hello", []) == "hello"
