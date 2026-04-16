from __future__ import annotations

import re

from pdf_parser.models import Price


PRICE_RE = re.compile(r"(?<!\+)\$(?:\d+|X)\b", re.IGNORECASE)
ONLY_PRICE_RE = re.compile(r"^\s*(?<!\+)(\$(?:\d+|X))\s*$", re.IGNORECASE)


def normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def normalize_name(value: str) -> str:
    value = normalize_whitespace(value)
    return value.strip(" -\t")


def normalize_description(lines: list[str]) -> str:
    return normalize_whitespace(" ".join(line.strip() for line in lines if line.strip()))


def parse_price(value: str | None) -> Price:
    if value is None:
        return None

    token = normalize_whitespace(value).upper()
    if not token:
        return None
    if token == "$X":
        return "$X"
    if token.startswith("$") and token[1:].isdigit():
        return int(token[1:])
    return token


def is_mostly_upper(value: str) -> bool:
    letters = [char for char in value if char.isalpha()]
    if not letters:
        return False
    upper_letters = [char for char in letters if char.upper() == char]
    return len(upper_letters) / len(letters) >= 0.8
