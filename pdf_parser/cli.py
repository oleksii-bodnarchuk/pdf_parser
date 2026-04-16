from __future__ import annotations

import argparse
import json
from pathlib import Path

from pdf_parser.extractor import extract_lines
from pdf_parser.models import MenuItem, MenuProfile, MenuStructure
from pdf_parser.parser import parse_menu
from pdf_parser.profiles import ESPN_BET_PROFILE, PROFILES, get_profile
from pdf_parser.structure import StructureDetectionError, detect_menu_structure


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Parse menu items from a PDF into JSON.")
    parser.add_argument("input_pdf", type=Path, help="Path to the source PDF menu.")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("output/espn_bet.json"),
        help="Path for the generated JSON file.",
    )
    parser.add_argument(
        "--structure-output",
        type=Path,
        default=None,
        help="Path for the auto-detected category structure JSON.",
    )
    parser.add_argument(
        "--profile",
        choices=sorted(PROFILES),
        default=ESPN_BET_PROFILE.name,
        help="Menu layout profile to use for extraction thresholds and filters.",
    )
    structure_group = parser.add_mutually_exclusive_group()
    structure_group.add_argument(
        "--auto-structure",
        action="store_true",
        default=True,
        help="Detect menu categories from the PDF before parsing items. This is the default.",
    )
    structure_group.add_argument(
        "--profile-categories",
        dest="auto_structure",
        action="store_false",
        help="Use the selected profile's manually listed categories instead of auto-detection.",
    )
    return parser


def run(
    input_pdf: Path,
    output: Path,
    profile: MenuProfile = ESPN_BET_PROFILE,
    auto_structure: bool = True,
    structure_output: Path | None = None,
) -> list[dict[str, object]]:
    lines = extract_lines(input_pdf, profile)
    structure = detect_menu_structure(lines, profile) if auto_structure else None
    items = parse_menu(lines, profile, structure)
    payload = [item.to_dict() for item in items]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if structure is not None:
        structure_path = structure_output or _default_structure_output(output)
        structure_path.parent.mkdir(parents=True, exist_ok=True)
        structure_path.write_text(
            json.dumps(
                _structure_payload(profile, structure, items),
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
    return payload


def _default_structure_output(output: Path) -> Path:
    return output.with_name(f"{output.stem}_structure.json")


def _structure_payload(
    profile: MenuProfile,
    structure: MenuStructure,
    items: list[MenuItem],
) -> dict[str, object]:
    item_counts = _item_counts_by_path(items)
    return {
        "profile": profile.name,
        "confidence": structure.confidence,
        "category_count": len(structure.category_paths_by_index),
        "no_price_item_categories": sorted(structure.no_price_item_categories),
        "categories": [
            {
                "name": category.text,
                "role": category.role,
                "path": list(category.path),
                "confidence": category.confidence,
                "line_index": category.line_index,
                "item_count": item_counts.get(category.path, 0),
            }
            for category in structure.detected_categories
        ],
    }


def _item_counts_by_path(items: list[MenuItem]) -> dict[tuple[str, ...], int]:
    counts: dict[tuple[str, ...], int] = {}
    for item in items:
        key = item.category_path or (item.category,)
        counts[key] = counts.get(key, 0) + 1
    return counts


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        payload = run(
            args.input_pdf,
            args.output,
            get_profile(args.profile),
            args.auto_structure,
            args.structure_output,
        )
    except StructureDetectionError as exc:
        parser.error(str(exc))
    print(f"Wrote {len(payload)} menu items to {args.output}")


if __name__ == "__main__":
    main()
