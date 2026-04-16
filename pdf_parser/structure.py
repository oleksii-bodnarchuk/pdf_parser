from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from pdf_parser.models import DetectedCategory, ExtractedLine, MenuProfile, MenuStructure
from pdf_parser.normalization import (
    ONLY_PRICE_RE,
    PRICE_RE,
    is_mostly_upper,
    normalize_name,
    normalize_whitespace,
)


class StructureDetectionError(ValueError):
    """Raised when a PDF does not expose enough menu structure signals."""


@dataclass(frozen=True)
class _ItemContext:
    has_items: bool
    kind: str
    confidence: float


@dataclass(frozen=True)
class _Candidate:
    index: int
    text: str
    role: str
    context: _ItemContext
    strong: bool


def detect_menu_structure(
    lines: list[ExtractedLine],
    profile: MenuProfile,
) -> MenuStructure:
    heading_min_size = _dynamic_heading_min_size(lines, profile)
    strong_indexes = {
        index
        for index, line in enumerate(lines)
        if _is_heading_candidate(line, profile, heading_min_size, strong_only=True)
    }
    weak_indexes = _weak_subheading_indexes(lines, profile, strong_indexes, heading_min_size)
    candidate_indexes = sorted(strong_indexes | weak_indexes)
    candidates = _classify_candidates(lines, profile, candidate_indexes, heading_min_size)

    leaf_candidates = [candidate for candidate in candidates if candidate.role == "leaf"]
    if len(leaf_candidates) < 2:
        raise StructureDetectionError("Auto-structure found fewer than two menu categories.")

    detected_categories = _build_detected_categories(lines, candidates)
    confidence = sum(category.confidence for category in detected_categories) / len(
        detected_categories
    )
    if confidence < 0.55:
        raise StructureDetectionError(
            f"Auto-structure confidence is too low ({confidence:.2f})."
        )

    category_paths_by_index = {
        category.line_index: category.path
        for category in detected_categories
        if category.role == "leaf"
    }
    no_price_item_categories = frozenset(
        candidate.text
        for candidate in candidates
        if candidate.role == "leaf" and candidate.context.kind == "no_price_list"
    )
    return MenuStructure(
        category_paths_by_index=category_paths_by_index,
        no_price_item_categories=no_price_item_categories,
        detected_categories=detected_categories,
        confidence=confidence,
        category_line_indexes=frozenset(category.line_index for category in detected_categories),
    )


def _dynamic_heading_min_size(lines: list[ExtractedLine], profile: MenuProfile) -> float:
    body_sizes = [
        round(line.max_size, 1)
        for line in lines
        if 0 < line.max_size < profile.heading_min_size
    ]
    if not body_sizes:
        body_sizes = [round(line.max_size, 1) for line in lines if line.max_size > 0]
    if not body_sizes:
        return profile.heading_min_size
    body_size = Counter(body_sizes).most_common(1)[0][0]
    return max(profile.heading_min_size, body_size + 3)


def _weak_subheading_indexes(
    lines: list[ExtractedLine],
    profile: MenuProfile,
    strong_indexes: set[int],
    heading_min_size: float,
) -> set[int]:
    weak_indexes: set[int] = set()
    sorted_strong = sorted(strong_indexes)

    for position, strong_index in enumerate(sorted_strong):
        stop = sorted_strong[position + 1] if position + 1 < len(sorted_strong) else len(lines)
        next_index = _next_relevant_line_index(lines, profile, strong_index + 1, stop)
        if next_index is None or next_index in strong_indexes:
            continue
        line = lines[next_index]
        if not _is_heading_candidate(line, profile, heading_min_size, strong_only=False):
            continue
        context = _item_context_after(lines, profile, next_index, stop)
        if context.has_items and context.kind != "no_price_list":
            weak_indexes.add(next_index)

    return weak_indexes


def _classify_candidates(
    lines: list[ExtractedLine],
    profile: MenuProfile,
    candidate_indexes: list[int],
    heading_min_size: float,
) -> list[_Candidate]:
    candidates: list[_Candidate] = []

    for position, index in enumerate(candidate_indexes):
        stop = (
            candidate_indexes[position + 1]
            if position + 1 < len(candidate_indexes)
            else len(lines)
        )
        context = _item_context_after(lines, profile, index, stop)
        text = normalize_name(lines[index].text)
        strong = lines[index].max_size >= heading_min_size

        if context.has_items:
            candidates.append(_Candidate(index, text, "leaf", context, strong))
            continue

        if position + 1 >= len(candidate_indexes):
            continue
        child_index = candidate_indexes[position + 1]
        child_stop = (
            candidate_indexes[position + 2] if position + 2 < len(candidate_indexes) else len(lines)
        )
        child_context = _item_context_after(lines, profile, child_index, child_stop)
        if child_context.has_items:
            confidence = 0.7 if strong else 0.55
            candidates.append(
                _Candidate(index, text, "parent", _ItemContext(True, "parent", confidence), strong)
            )

    return candidates


def _build_detected_categories(
    lines: list[ExtractedLine],
    candidates: list[_Candidate],
) -> tuple[DetectedCategory, ...]:
    detected: list[DetectedCategory] = []
    active_parent: _Candidate | None = None

    for candidate in candidates:
        if candidate.role == "parent":
            active_parent = candidate
            detected.append(
                DetectedCategory(
                    text=candidate.text,
                    line_index=candidate.index,
                    path=(candidate.text,),
                    confidence=candidate.context.confidence,
                    role="parent",
                )
            )
            continue

        parent_applies = active_parent is not None and _parent_scope_applies(
            lines[active_parent.index], lines[candidate.index]
        )
        path = (
            (active_parent.text, candidate.text)
            if parent_applies and active_parent
            else (candidate.text,)
        )
        detected.append(
            DetectedCategory(
                text=candidate.text,
                line_index=candidate.index,
                path=path,
                confidence=candidate.context.confidence,
                role="leaf",
            )
        )

        if active_parent and not parent_applies:
            active_parent = None

    return tuple(detected)


def _parent_scope_applies(parent_line: ExtractedLine, child_line: ExtractedLine) -> bool:
    if parent_line.page_number != child_line.page_number:
        return False
    if "MENU" in parent_line.text.upper():
        return True
    return parent_line.column == child_line.column


def _item_context_after(
    lines: list[ExtractedLine],
    profile: MenuProfile,
    index: int,
    stop: int,
) -> _ItemContext:
    uppercase_no_price_lines = 0
    section_price_seen = False

    for next_index in range(index + 1, stop):
        text = normalize_whitespace(lines[next_index].text)
        if not text or _is_section_note(text, profile):
            continue

        if PRICE_RE.search(text):
            return _ItemContext(True, "priced", 0.95)

        if ONLY_PRICE_RE.match(text):
            section_price_seen = True
            continue

        if section_price_seen and _looks_like_item_name(lines[next_index]):
            return _ItemContext(True, "section_price", 0.85)

        if _looks_like_item_name(lines[next_index]):
            uppercase_no_price_lines += 1
            continue

        if uppercase_no_price_lines:
            break

    if uppercase_no_price_lines >= 2:
        return _ItemContext(True, "no_price_list", 0.7)
    return _ItemContext(False, "none", 0.0)


def _next_relevant_line_index(
    lines: list[ExtractedLine],
    profile: MenuProfile,
    start: int,
    stop: int,
) -> int | None:
    for index in range(start, stop):
        text = normalize_whitespace(lines[index].text)
        if text and not _is_section_note(text, profile):
            return index
    return None


def _is_heading_candidate(
    line: ExtractedLine,
    profile: MenuProfile,
    heading_min_size: float,
    strong_only: bool,
) -> bool:
    text = normalize_name(line.text)
    if not text or PRICE_RE.search(text):
        return False
    if _is_section_note(text, profile):
        return False
    if strong_only:
        return line.max_size >= heading_min_size and is_mostly_upper(text)
    return is_mostly_upper(text)


def _looks_like_item_name(line: ExtractedLine) -> bool:
    text = normalize_name(line.text)
    return bool(text) and not PRICE_RE.search(text) and is_mostly_upper(text)


def _is_section_note(text: str, profile: MenuProfile) -> bool:
    folded = text.casefold()
    return any(folded.startswith(prefix) for prefix in profile.section_note_prefixes)
