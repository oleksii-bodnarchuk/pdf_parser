from __future__ import annotations

import argparse
import json
from pathlib import Path

from pdf_parser.extractor import extract_lines
from pdf_parser.parser import parse_menu


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
    return parser


def run(input_pdf: Path, output: Path) -> list[dict[str, object]]:
    lines = extract_lines(input_pdf)
    items = parse_menu(lines)
    payload = [item.to_dict() for item in items]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    args = build_parser().parse_args()
    payload = run(args.input_pdf, args.output)
    print(f"Wrote {len(payload)} menu items to {args.output}")


if __name__ == "__main__":
    main()
