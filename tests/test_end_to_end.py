import json
from pathlib import Path

import pytest

from pdf_parser.cli import run
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


@pytest.mark.skipif(not SAMPLE_PDF.exists(), reason="sample PDF is not available")
def test_cli_run_defaults_to_auto_structure(tmp_path: Path) -> None:
    output = tmp_path / "menu.json"
    structure_output = tmp_path / "menu_structure.json"
    payload = run(SAMPLE_PDF, output)

    assert len(payload) == 98
    assert output.exists()
    assert structure_output.exists()

    structure_payload = json.loads(structure_output.read_text(encoding="utf-8"))
    assert structure_payload["category_count"] >= 10
    assert any(
        category["path"]
        == ["AIN’T NO THING BUT A CHICKEN…", "JUMBO CHICKEN WINGS BREADED CHICKEN TENDERS"]
        and category["item_count"] > 0
        for category in structure_payload["categories"]
    )
    assert any(
        item["category"] == "JUMBO CHICKEN WINGS BREADED CHICKEN TENDERS"
        and item["category_path"]
        for item in payload
    )


@pytest.mark.skipif(not SAMPLE_PDF.exists(), reason="sample PDF is not available")
def test_cli_run_can_write_custom_structure_output(tmp_path: Path) -> None:
    structure_output = tmp_path / "categories.json"

    run(SAMPLE_PDF, tmp_path / "menu.json", structure_output=structure_output)

    assert structure_output.exists()


@pytest.mark.skipif(not SAMPLE_PDF.exists(), reason="sample PDF is not available")
def test_cli_run_skips_structure_output_with_profile_categories(tmp_path: Path) -> None:
    structure_output = tmp_path / "menu_structure.json"

    run(SAMPLE_PDF, tmp_path / "menu.json", auto_structure=False)

    assert not structure_output.exists()
