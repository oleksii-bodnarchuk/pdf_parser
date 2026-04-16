from pathlib import Path

import pytest

from pdf_parser.extractor import extract_lines
from pdf_parser.parser import parse_menu
from pdf_parser.profiles import ESPN_BET_PROFILE
from pdf_parser.structure import detect_menu_structure


SAMPLE_PDF = Path(__file__).resolve().parents[1] / "pdf_menu" / "espn_bet.pdf"


@pytest.mark.skipif(not SAMPLE_PDF.exists(), reason="sample PDF is not available")
def test_sample_pdf_smoke_parse() -> None:
    items = parse_menu(extract_lines(SAMPLE_PDF))

    assert len(items) == 98
    assert all(item.category for item in items)
    assert all(item.dish_name for item in items)
    assert any(
        item.category == "BURGERS"
        and item.dish_name == "ALL AMERICAN BURGER"
        and item.price == 17
        for item in items
    )
    assert any(
        item.category == "SIGNATURE COCKTAILS"
        and item.dish_name == "DILLINOIS"
        and item.price == "$X"
        for item in items
    )
    assert items[-1].dish_name == "RED BULL YELLOW EDITION (TROPICAL)"


@pytest.mark.skipif(not SAMPLE_PDF.exists(), reason="sample PDF is not available")
def test_sample_pdf_auto_structure_smoke_parse() -> None:
    lines = extract_lines(SAMPLE_PDF)
    structure = detect_menu_structure(lines, ESPN_BET_PROFILE)
    items = parse_menu(lines, ESPN_BET_PROFILE, structure)

    assert len(items) == 98
    assert any(
        item.category == "JUMBO CHICKEN WINGS BREADED CHICKEN TENDERS"
        and item.dish_name == "6 WINGS"
        and item.category_path
        for item in items
    )
    assert any(
        item.category == "BURGERS"
        and item.dish_name == "ALL AMERICAN BURGER"
        and item.price == 17
        for item in items
    )
