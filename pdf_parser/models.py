from __future__ import annotations

from dataclasses import asdict, dataclass


Price = int | str | None


@dataclass(frozen=True)
class MenuProfile:
    name: str
    known_categories: frozenset[str]
    no_price_item_categories: frozenset[str]
    section_note_prefixes: tuple[str, ...]
    ignored_line_prefixes: tuple[str, ...]
    ignored_line_contains: tuple[str, ...]
    word_x_tolerance: float = 2.0
    word_y_tolerance: float = 3.0
    row_y_tolerance: float = 3.0
    heading_min_size: float = 13.5
    column_count: int = 2
    segment_gap_min: float = 96.0


@dataclass(frozen=True)
class MenuItem:
    category: str
    dish_name: str
    price: Price
    description: str
    dish_id: str
    category_path: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ExtractedLine:
    text: str
    page_number: int
    column: int
    top: float
    x0: float
    x1: float
    max_size: float
    segments: tuple[str, ...] = ()


@dataclass(frozen=True)
class DetectedCategory:
    text: str
    line_index: int
    path: tuple[str, ...]
    confidence: float
    role: str


@dataclass(frozen=True)
class MenuStructure:
    category_paths_by_index: dict[int, tuple[str, ...]]
    no_price_item_categories: frozenset[str]
    detected_categories: tuple[DetectedCategory, ...]
    confidence: float
    category_line_indexes: frozenset[int]
