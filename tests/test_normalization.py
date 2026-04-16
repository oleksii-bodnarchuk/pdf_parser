from pdf_parser.normalization import normalize_description, normalize_whitespace, parse_price


def test_parse_numeric_price_as_int() -> None:
    assert parse_price("$17") == 17


def test_parse_placeholder_price() -> None:
    assert parse_price("$X") == "$X"


def test_parse_missing_price() -> None:
    assert parse_price(None) is None


def test_normalize_multiline_description() -> None:
    assert (
        normalize_description([" lettuce, tomato,  ", " pickles, brioche bun "])
        == "lettuce, tomato, pickles, brioche bun"
    )


def test_normalize_whitespace() -> None:
    assert normalize_whitespace("ALL   AMERICAN\nBURGER") == "ALL AMERICAN BURGER"
