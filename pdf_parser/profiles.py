from __future__ import annotations

from pdf_parser.models import MenuProfile


ESPN_BET_PROFILE = MenuProfile(
    name="espn_bet",
    known_categories=frozenset(
        {
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
    ),
    no_price_item_categories=frozenset(
        {
            "SIGNATURE SAUCES",
            "JUMBO CHICKEN WINGS BREADED CHICKEN TENDERS",
            "ENERGY",
        }
    ),
    section_note_prefixes=(
        "served with",
        "gluten-free",
        "sub beyond",
    ),
    ignored_line_prefixes=(
        "* contains",
        "shellfish or eggs",
    ),
    ignored_line_contains=("foodborne illness",),
    segment_gap_min=200.0,
)

PROFILES = {ESPN_BET_PROFILE.name: ESPN_BET_PROFILE}


def get_profile(name: str) -> MenuProfile:
    try:
        return PROFILES[name]
    except KeyError as exc:
        available = ", ".join(sorted(PROFILES))
        raise ValueError(f"Unknown profile {name!r}. Available profiles: {available}") from exc
