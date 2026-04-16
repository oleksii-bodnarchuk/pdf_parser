from __future__ import annotations

from dataclasses import asdict, dataclass


Price = int | str | None


@dataclass(frozen=True)
class MenuItem:
    category: str
    dish_name: str
    price: Price
    description: str
    dish_id: str

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
