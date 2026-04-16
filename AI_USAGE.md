# AI Usage Reflection

This project used AI as a development assistant, not as an unattended generator. The implementation choices were checked against the provided PDF, local command output, and automated tests.

## Where AI helped

- Interpreted the assignment requirements and narrowed the output shape to a small reproducible CLI that writes JSON.
- Compared PDF parsing approaches and selected a coordinate-aware `pdfplumber` workflow instead of plain text extraction, because the menu layout depends on columns, heading sizes, and positioned prices.
- Helped design the first parsing pipeline: extract positioned words, rebuild visual lines, split by columns, detect headings, group items, attach prices, and normalize descriptions.
- Suggested heuristics for edge cases in the supplied menu, including two-column ordering, section headers, multi-line descriptions, multiple priced items on one line, `$X` placeholder prices, and no-price item lists.
- Helped evolve the parser from profile-only categories to an auto-structure pass that detects category hierarchy and writes a sidecar structure JSON.
- Helped draft and revise documentation so a reviewer can install the tool, run it on Windows/macOS/Linux, inspect outputs, and understand the parser limits.

## What was verified manually

- The supplied sample PDF is machine-generated text with extractable word coordinates, so OCR was intentionally skipped.
- The CLI path was exercised through `uv run parse-menu ...`, including the default auto-structure behavior and custom output paths.
- The generated item JSON and structure JSON were inspected for expected fields, category paths, placeholder prices, missing prices, and stable item IDs.
- Automated tests cover normalization, item parsing, structure detection, and end-to-end smoke parsing for the bundled sample PDF when it is available.

## Human decisions and trade-offs

- Kept the project as a CLI instead of adding a web API or UI, because the assignment asks for a small reproducible parser and JSON output.
- Chose deterministic heuristics over an LLM-based extraction step so the parser can run locally, produce repeatable output, and avoid sending menu data to an external service.
- Kept the profile system lightweight. Profiles tune layout thresholds, ignored text, and optional known categories without turning the prototype into a full rules engine.
- Left OCR out of scope. Adding OCR would require extra dependencies, slower runtime, and a separate validation path for noisy image text.

## Known gaps

- The parser is tuned for the supplied ESPN BET-style menu layout and similar machine-generated two-column menus.
- Scanned image-only PDFs are not supported unless OCR is run before this tool.
- Very unusual layouts may need a new or adjusted `MenuProfile`, especially if category headings are not uppercase, prices are far from item names, or dense sauce/rub lists use unusual spacing.
- Auto-structure detection uses layout confidence rather than semantic knowledge. If confidence is too low, use `--profile-categories` for a known profile or add a profile for the new layout.
- The parser extracts menu text and prices, but it does not validate culinary meaning, currency rules, allergens, or business-specific menu taxonomy.

## Reproducibility notes

- Dependencies are declared in `pyproject.toml` and locked in `uv.lock`.
- The CLI entry point is `parse-menu`.
- Tests can be run with `uv run pytest`.
- Main outputs are written as UTF-8 JSON with `ensure_ascii=False` to preserve menu punctuation and symbols.
