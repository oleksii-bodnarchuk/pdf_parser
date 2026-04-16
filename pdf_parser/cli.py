from __future__ import annotations

import argparse
import json
from pathlib import Path

from pdf_parser.extractor import extract_lines
from pdf_parser.models import MenuProfile
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
        "--profile",
        choices=sorted(PROFILES),
        default=ESPN_BET_PROFILE.name,
        help="Menu parsing profile to use.",
    )
    parser.add_argument(
        "--auto-structure",
        action="store_true",
        help="Detect menu categories from the PDF before parsing items.",
    )
    return parser


def run(
    input_pdf: Path,
    output: Path,
    profile: MenuProfile = ESPN_BET_PROFILE,
    auto_structure: bool = False,
) -> list[dict[str, object]]:
    lines = extract_lines(input_pdf, profile)
    structure = detect_menu_structure(lines, profile) if auto_structure else None
    items = parse_menu(lines, profile, structure)
    payload = [item.to_dict() for item in items]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        payload = run(args.input_pdf, args.output, get_profile(args.profile), args.auto_structure)
    except StructureDetectionError as exc:
        parser.error(str(exc))
    print(f"Wrote {len(payload)} menu items to {args.output}")


if __name__ == "__main__":
    main()
