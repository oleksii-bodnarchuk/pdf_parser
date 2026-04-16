# Menu PDF Parser

Small take-home prototype that extracts menu items from a two-column PDF and writes normalized JSON.

## Setup

```powershell
uv sync
```

## Run

```powershell
uv run parse-menu "path to your pdf menu" --output output\menu.json
```

By default, the parser performs a first-pass category detector and then uses the detected categories to build the item list.
It also writes a sidecar structure file next to the output, for example `output\menu_structure.json`, with the detected categories, hierarchy paths, confidence, and item counts.

To use manually listed categories from a custom profile instead, opt in explicitly:

```powershell
uv run parse-menu "path to your pdf menu" --output output\menu.json --profile espn_bet --profile-categories
```

To choose a custom path for the sidecar structure file:

```powershell
uv run parse-menu "path to your pdf menu" --output output\menu.json --structure-output output\categories.json
```

The generated JSON is an array of objects with:

- `category`
- `dish_name`
- `price`
- `description`
- `dish_id`
- `category_path`

Numeric dollar prices are stored as integers, placeholder prices are stored as `"$X"`, and missing prices are stored as `null`.

## Tests

```powershell
uv run pytest
```

## Notes

The parser is intentionally heuristic. By default, it uses pdfplumber word coordinates, splits each page into columns, reconstructs visual lines, detects category headings, then groups item lines, prices, and descriptions.

Profiles are still useful for custom layout thresholds, filters, and optional manually listed categories. To support a similar machine-generated menu with a known special layout, add a new `MenuProfile` in `pdf_parser/profiles.py` and run the CLI with `--profile`; add `--profile-categories` only when you want to bypass auto-detected category names.

It does not perform OCR.
