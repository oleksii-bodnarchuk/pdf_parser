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

The generated JSON is an array of objects with:

- `category`
- `dish_name`
- `price`
- `description`
- `dish_id`

Numeric dollar prices are stored as integers, placeholder prices are stored as `"$X"`, and missing prices are stored as `null`.

## Tests

```powershell
uv run pytest
```

## Notes

The parser is intentionally heuristic and tuned through small menu profiles. The default `espn_bet` profile uses pdfplumber word coordinates, splits each page into left/right columns, reconstructs visual lines, then groups headers, item lines, prices, and descriptions.

To support another similar machine-generated menu, add a new `MenuProfile` in `pdf_parser/profiles.py` with its category names and layout thresholds, then run the CLI with `--profile`.

It does not perform OCR.
