# Menu PDF Parser

Small take-home prototype that extracts menu items from a two-column PDF and writes normalized JSON.

## Setup

```powershell
uv sync
```

## Run

```powershell
uv run parse-menu "path to your pdf menu" --output output\espn_bet.json
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

The parser is intentionally heuristic and tuned for this sample menu. It uses pdfplumber word coordinates, splits each page into left/right columns, reconstructs visual lines, then groups headers, item lines, prices, and descriptions. It does not perform OCR.
