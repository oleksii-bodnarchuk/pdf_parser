from __future__ import annotations

from pathlib import Path
from typing import Any

import pdfplumber

from pdf_parser.models import ExtractedLine
from pdf_parser.normalization import normalize_whitespace


def extract_lines(pdf_path: str | Path) -> list[ExtractedLine]:
    """Extract visually ordered lines by page and column."""
    lines: list[ExtractedLine] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page_index, page in enumerate(pdf.pages, start=1):
            words = page.extract_words(
                x_tolerance=2,
                y_tolerance=3,
                keep_blank_chars=False,
                use_text_flow=False,
                extra_attrs=["size"],
            )
            split_x = page.width / 2
            for column_index, predicate in enumerate(
                (
                    lambda word, split=split_x: word["x0"] < split,
                    lambda word, split=split_x: word["x0"] >= split,
                )
            ):
                column_words = [word for word in words if predicate(word)]
                lines.extend(_group_column_words(column_words, page_index, column_index))

    return [
        line
        for line in sorted(lines, key=lambda item: (item.page_number, item.column, item.top, item.x0))
        if not _is_footer_or_warning(line.text)
    ]


def _group_column_words(
    words: list[dict[str, Any]],
    page_number: int,
    column: int,
    y_tolerance: float = 3.0,
) -> list[ExtractedLine]:
    rows: list[dict[str, Any]] = []
    for word in sorted(words, key=lambda item: (item["top"], item["x0"])):
        row = _find_row(rows, word["top"], y_tolerance)
        if row is None:
            rows.append({"top": word["top"], "words": [word]})
        else:
            row["words"].append(word)
            row["top"] = (row["top"] + word["top"]) / 2

    extracted: list[ExtractedLine] = []
    for row in rows:
        row_words = sorted(row["words"], key=lambda item: item["x0"])
        text = normalize_whitespace(" ".join(word["text"] for word in row_words))
        if not text:
            continue
        extracted.append(
            ExtractedLine(
                text=text,
                page_number=page_number,
                column=column,
                top=float(min(word["top"] for word in row_words)),
                x0=float(min(word["x0"] for word in row_words)),
                x1=float(max(word["x1"] for word in row_words)),
                max_size=float(max(word.get("size") or 0 for word in row_words)),
            )
        )
    return extracted


def _find_row(rows: list[dict[str, Any]], top: float, y_tolerance: float) -> dict[str, Any] | None:
    for row in rows:
        if abs(row["top"] - top) <= y_tolerance:
            return row
    return None


def _is_footer_or_warning(text: str) -> bool:
    normalized = text.casefold()
    return (
        normalized.startswith("* contains")
        or "foodborne illness" in normalized
        or normalized.startswith("shellfish or eggs")
    )
