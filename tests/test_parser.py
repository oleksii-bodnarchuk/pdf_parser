from dataclasses import replace

import pytest

from pdf_parser.cli import build_parser
from pdf_parser.models import ExtractedLine
from pdf_parser.parser import parse_menu
from pdf_parser.profiles import ESPN_BET_PROFILE


def line(
    text: str,
    top: float,
    max_size: float = 10.0,
    segments: tuple[str, ...] = (),
) -> ExtractedLine:
    return ExtractedLine(
        text=text,
        page_number=1,
        column=0,
        top=top,
        x0=36.0,
        x1=378.0,
        max_size=max_size,
        segments=segments,
    )


def test_parse_priced_item_with_description() -> None:
    items = parse_menu(
        [
            line("BURGERS", 10, 16),
            line("ALL AMERICAN BURGER $17", 20),
            line("7 oz. steakburger, choice of cheese", 30, 8),
        ]
    )

    assert items[0].category == "BURGERS"
    assert items[0].dish_name == "ALL AMERICAN BURGER"
    assert items[0].price == 17
    assert items[0].description == "7 oz. steakburger, choice of cheese"
    assert items[0].dish_id == "001"


def test_parse_missing_price_item_in_no_price_section() -> None:
    items = parse_menu(
        [
            line("SIGNATURE SAUCES", 10, 16),
            line("GARLIC PARMESAN", 20),
        ]
    )

    assert items[0].dish_name == "GARLIC PARMESAN"
    assert items[0].price is None


def test_parse_placeholder_price() -> None:
    items = parse_menu(
        [
            line("FLIGHTS", 10, 16),
            line("4 WINGS & 4 SAUCES $X", 20),
        ]
    )

    assert items[0].price == "$X"


def test_parse_multiple_priced_items_on_one_line() -> None:
    items = parse_menu(
        [
            line("SIDES", 10, 16),
            line("COLESLAW $4 ONION PETALS $8", 20),
        ]
    )

    assert [item.dish_name for item in items] == ["COLESLAW", "ONION PETALS"]
    assert [item.price for item in items] == [4, 8]


def test_custom_profile_can_add_category_without_parser_changes() -> None:
    profile = replace(
        ESPN_BET_PROFILE,
        name="custom",
        known_categories=ESPN_BET_PROFILE.known_categories | frozenset({"SNACKS"}),
    )

    items = parse_menu(
        [
            line("SNACKS", 10, 16),
            line("CRISPY PICKLES $9", 20),
        ],
        profile,
    )

    assert items[0].category == "SNACKS"
    assert items[0].dish_name == "CRISPY PICKLES"
    assert items[0].price == 9


def test_no_price_section_can_split_explicit_line_segments() -> None:
    items = parse_menu(
        [
            line("SIGNATURE SAUCES", 10, 16),
            line(
                "GARLIC PARMESAN BACON BOURBON",
                20,
                segments=("GARLIC PARMESAN", "BACON BOURBON"),
            ),
        ]
    )

    assert [item.dish_name for item in items] == ["GARLIC PARMESAN", "BACON BOURBON"]
    assert [item.price for item in items] == [None, None]


def test_cli_accepts_profile_option() -> None:
    args = build_parser().parse_args(["menu.pdf", "--profile", "espn_bet"])

    assert args.profile == "espn_bet"


def test_cli_rejects_unknown_profile() -> None:
    with pytest.raises(SystemExit):
        build_parser().parse_args(["menu.pdf", "--profile", "unknown"])
