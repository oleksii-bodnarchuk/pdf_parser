# Menu PDF Parser

Small take-home prototype that extracts menu items from a two-column PDF and writes normalized JSON.

## Setup

```powershell
uv sync
```

## Run

```powershell
uv run parse-menu "path to your pdf menu" --output output\espn_bet.json --profile espn_bet
```

For similar restaurant menus where category names are not known yet, enable the first-pass category detector:

```powershell
uv run parse-menu "path to your pdf menu" --output output\menu.json --auto-structure
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

The parser is intentionally heuristic and tuned through small menu profiles. The default `espn_bet` profile uses pdfplumber word coordinates, splits each page into left/right columns, reconstructs visual lines, then groups headers, item lines, prices, and descriptions.

To support another similar machine-generated menu, add a new `MenuProfile` in `pdf_parser/profiles.py` with its category names and layout thresholds, then run the CLI with `--profile`. If the PDF has clear heading typography, `--auto-structure` can detect category names first and use the profile only for layout thresholds and filtering.

It does not perform OCR.
