from __future__ import annotations

from dataclasses import dataclass, field

from pdf_parser.models import ExtractedLine, MenuItem, Price
from pdf_parser.normalization import (
    ONLY_PRICE_RE,
    PRICE_RE,
    is_mostly_upper,
    normalize_description,
    normalize_name,
    normalize_whitespace,
    parse_price,
)


KNOWN_CATEGORIES = {
    "LEADING OFF",
    "SLIDER TOWERS",
    "AIN'T NO THING BUT A CHICKEN...",
    "AIN’T NO THING BUT A CHICKEN…",
    "JUMBO CHICKEN WINGS BREADED CHICKEN TENDERS",
    "SIGNATURE SAUCES",
    "FLIGHTS",
    "SALADS & SOUP",
    "HANDHELDS",
    "BURGERS",
    "MAIN EVENT",
    "SIDES",
    "OVERTIME",
    "DRINK MENU",
    "SIGNATURE COCKTAILS",
    "ZERO PROOF",
    "DRAFT BEER",
    "BOTTLES & CANS",
    "WINES",
    "ENERGY",
}

NO_PRICE_ITEM_CATEGORIES = {
    "SIGNATURE SAUCES",
    "JUMBO CHICKEN WINGS BREADED CHICKEN TENDERS",
    "ENERGY",
}

SECTION_NOTE_PREFIXES = (
    "served with",
    "gluten-free",
    "sub beyond",
)


@dataclass
class _DraftItem:
    category: str
    dish_name: str
    price: Price
    description_lines: list[str] = field(default_factory=list)

    def build(self, dish_id: int) -> MenuItem:
        return MenuItem(
            category=self.category,
            dish_name=self.dish_name,
            price=self.price,
            description=normalize_description(self.description_lines),
            dish_id=f"{dish_id:03d}",
        )


def parse_menu(lines: list[ExtractedLine]) -> list[MenuItem]:
    items: list[MenuItem] = []
    current_category: str | None = None
    current_item: _DraftItem | None = None
    section_price: Price = None

    def flush_current() -> None:
        nonlocal current_item
        if current_item is None:
            return
        if current_item.dish_name:
            items.append(current_item.build(len(items) + 1))
        current_item = None

    for line in lines:
        text = normalize_whitespace(line.text)
        if not text:
            continue

        only_price = ONLY_PRICE_RE.match(text)
        if only_price and current_category:
            section_price = parse_price(only_price.group(1))
            continue

        if _is_category_line(line):
            flush_current()
            current_category = normalize_name(text)
            section_price = None
            continue

        if current_category is None:
            continue

        priced_parts = _split_priced_items(text)
        if priced_parts:
            flush_current()
            for name, price in priced_parts[:-1]:
                items.append(
                    _DraftItem(current_category, normalize_name(name), parse_price(price)).build(
                        len(items) + 1
                    )
                )
            name, price = priced_parts[-1]
            current_item = _DraftItem(current_category, normalize_name(name), parse_price(price))
            continue

        if _is_section_note(text):
            continue

        if _is_no_price_item_line(text, current_category, line, section_price):
            flush_current()
            current_item = _DraftItem(current_category, normalize_name(text), section_price)
            continue

        if current_item is not None:
            current_item.description_lines.append(text)

    flush_current()
    return items


def _is_category_line(line: ExtractedLine) -> bool:
    text = normalize_name(line.text)
    if PRICE_RE.search(text):
        return False
    if text in KNOWN_CATEGORIES:
        return True
    return line.max_size >= 13.5 and is_mostly_upper(text)


def _split_priced_items(text: str) -> list[tuple[str, str]]:
    matches = list(PRICE_RE.finditer(text))
    if not matches:
        return []

    parts: list[tuple[str, str]] = []
    start = 0
    for match in matches:
        name = normalize_name(text[start : match.start()])
        if name:
            parts.append((name, match.group(0)))
        start = match.end()
    return parts


def _is_section_note(text: str) -> bool:
    folded = text.casefold()
    return any(folded.startswith(prefix) for prefix in SECTION_NOTE_PREFIXES)


def _is_no_price_item_line(
    text: str,
    current_category: str,
    line: ExtractedLine,
    section_price: Price,
) -> bool:
    return (
        current_category in NO_PRICE_ITEM_CATEGORIES
        or section_price is not None
        or (line.max_size < 13.5 and is_mostly_upper(text))
    )
