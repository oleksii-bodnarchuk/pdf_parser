import pytest

from pdf_parser.models import ExtractedLine
from pdf_parser.profiles import ESPN_BET_PROFILE
from pdf_parser.structure import StructureDetectionError, detect_menu_structure


def line(text: str, top: float, max_size: float = 10.0) -> ExtractedLine:
    return ExtractedLine(
        text=text,
        page_number=1,
        column=0,
        top=top,
        x0=36.0,
        x1=378.0,
        max_size=max_size,
    )


def test_detects_categories_without_known_category_names() -> None:
    structure = detect_menu_structure(
        [
            line("SNACKS", 10, 16),
            line("CRISPY PICKLES $9", 20),
            line("PLATES", 40, 16),
            line("ROAST CHICKEN $22", 50),
        ],
        ESPN_BET_PROFILE,
    )

    assert structure.category_paths_by_index == {0: ("SNACKS",), 2: ("PLATES",)}


def test_does_not_treat_no_price_list_items_as_categories() -> None:
    structure = detect_menu_structure(
        [
            line("SAUCES", 10, 16),
            line("GARLIC PARMESAN", 20),
            line("BUFFALO", 30),
            line("DESSERTS", 50, 16),
            line("CHOCOLATE CAKE $8", 60),
        ],
        ESPN_BET_PROFILE,
    )

    detected_texts = [category.text for category in structure.detected_categories]
    assert "SAUCES" in detected_texts
    assert "GARLIC PARMESAN" not in detected_texts
    assert structure.no_price_item_categories == frozenset({"SAUCES"})


def test_detects_weak_subcategory_after_parent_heading() -> None:
    structure = detect_menu_structure(
        [
            line("CHICKEN", 10, 16),
            line("WINGS & TENDERS", 20),
            line("6 WINGS $12", 30),
            line("DESSERTS", 50, 16),
            line("CHOCOLATE CAKE $8", 60),
        ],
        ESPN_BET_PROFILE,
    )

    assert structure.category_paths_by_index[1] == ("CHICKEN", "WINGS & TENDERS")


def test_detects_only_price_section_pattern() -> None:
    structure = detect_menu_structure(
        [
            line("ENERGY", 10, 16),
            line("$X", 20),
            line("RED BULL", 30),
            line("DESSERTS", 50, 16),
            line("CHOCOLATE CAKE $8", 60),
        ],
        ESPN_BET_PROFILE,
    )

    assert structure.category_paths_by_index[0] == ("ENERGY",)
    assert "ENERGY" not in structure.no_price_item_categories


def test_low_confidence_text_raises_error() -> None:
    with pytest.raises(StructureDetectionError):
        detect_menu_structure(
            [
                line("welcome to our restaurant", 10, 10),
                line("ask your server about specials", 20, 10),
            ],
            ESPN_BET_PROFILE,
        )
