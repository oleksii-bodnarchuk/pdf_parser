# AI Usage Reflection

- Used ChatGPT to inspect the assignment, compare PDF parsing libraries, and choose a coordinate-aware pdfplumber approach.
- Adapted the implementation toward a CLI because the assignment asks for a small reproducible script and JSON output rather than a web API.
- Used local PDF probing to confirm the sample is machine-generated text with positioned words, so OCR was intentionally skipped.
- Added heuristics for two-column ordering, section headers, multi-line descriptions, multiple priced items on one line, `$X` placeholders, and missing-price sections.
- Known gaps: this is tuned for the supplied menu layout; unusual future menus may need adjusted header detection or manual handling for dense sauce/rub lists.
