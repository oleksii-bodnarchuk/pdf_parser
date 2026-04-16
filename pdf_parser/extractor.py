from __future__ import annotations

from pathlib import Path
from typing import Any

import pdfplumber

from pdf_parser.models import ExtractedLine, MenuProfile
from pdf_parser.normalization import normalize_whitespace
from pdf_parser.profiles import ESPN_BET_PROFILE


def extract_lines(
    pdf_path: str | Path,
    profile: MenuProfile = ESPN_BET_PROFILE,
) -> list[ExtractedLine]:
    """Extract visually ordered lines by page and column."""
    lines: list[ExtractedLine] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page_index, page in enumerate(pdf.pages, start=1):
            words = page.extract_words(
                x_tolerance=profile.word_x_tolerance,
                y_tolerance=profile.word_y_tolerance,
                keep_blank_chars=False,
                use_text_flow=False,
                extra_attrs=["size"],
            )
            for column_index in range(profile.column_count):
                column_words = [
                    word
                    for word in words
                    if _column_for_word(word, page.width, profile.column_count) == column_index
                ]
                lines.extend(_group_column_words(column_words, page_index, column_index, profile))

    return [
        line
        for line in sorted(lines, key=lambda item: (item.page_number, item.column, item.top, item.x0))
        if not _is_ignored_line(line.text, profile)
    ]


def _column_for_word(word: dict[str, Any], page_width: float, column_count: int) -> int:
    if column_count <= 1:
        return 0
    column_width = page_width / column_count
    return min(int(word["x0"] / column_width), column_count - 1)


def _group_column_words(
    words: list[dict[str, Any]],
    page_number: int,
    column: int,
    profile: MenuProfile,
) -> list[ExtractedLine]:
    rows: list[dict[str, Any]] = []
    for word in sorted(words, key=lambda item: (item["top"], item["x0"])):
        row = _find_row(rows, word["top"], profile.row_y_tolerance)
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
        segments = tuple(_split_segments(row_words, profile.segment_gap_min))
        extracted.append(
            ExtractedLine(
                text=text,
                page_number=page_number,
                column=column,
                top=float(min(word["top"] for word in row_words)),
                x0=float(min(word["x0"] for word in row_words)),
                x1=float(max(word["x1"] for word in row_words)),
                max_size=float(max(word.get("size") or 0 for word in row_words)),
                segments=segments,
            )
        )
    return extracted


def _split_segments(words: list[dict[str, Any]], gap_min: float) -> list[str]:
    if not words:
        return []

    segments: list[str] = []
    current_words = [words[0]["text"]]
    previous_x1 = words[0]["x1"]

    for word in words[1:]:
        if word["x0"] - previous_x1 >= gap_min:
            segments.append(normalize_whitespace(" ".join(current_words)))
            current_words = []
        current_words.append(word["text"])
        previous_x1 = word["x1"]

    segments.append(normalize_whitespace(" ".join(current_words)))
    return [segment for segment in segments if segment]


def _find_row(rows: list[dict[str, Any]], top: float, y_tolerance: float) -> dict[str, Any] | None:
    for row in rows:
        if abs(row["top"] - top) <= y_tolerance:
            return row
    return None


def _is_ignored_line(text: str, profile: MenuProfile) -> bool:
    normalized = text.casefold()
    return any(normalized.startswith(prefix) for prefix in profile.ignored_line_prefixes) or any(
        snippet in normalized for snippet in profile.ignored_line_contains
    )
