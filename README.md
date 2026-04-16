# Menu PDF Parser

Small take-home prototype that extracts menu items from a machine-readable PDF menu and writes normalized JSON.

The project is packaged as a command-line tool called `parse-menu`. You do not need to know Python to run it: install `uv`, open a terminal in this folder, install the project dependencies, and run one command against a PDF file.

## What it produces

The main output is a JSON array where each menu item has:

- `category`
- `dish_name`
- `price`
- `description`
- `dish_id`
- `category_path`

Numeric dollar prices are stored as integers, placeholder prices are stored as `"$X"`, and missing prices are stored as `null`.

By default, the parser also writes a second JSON file next to the main output. For example, if the main output is `output/menu.json`, the structure file is `output/menu_structure.json`. That file contains the detected categories, hierarchy paths, confidence scores, and item counts.

## Requirements

- Windows 10+, macOS, or Linux
- A terminal application:
  - Windows: PowerShell
  - macOS: Terminal
  - Linux: Terminal
- Internet access for the first dependency install
- A machine-readable PDF menu. Scanned image-only PDFs are not supported because this tool does not perform OCR.

The project requires Python 3.12 or newer, but `uv` can download and manage a compatible Python automatically on most systems.

## 1. Install uv

`uv` is the Python project manager used by this repository. It creates the virtual environment and installs all dependencies from `pyproject.toml` and `uv.lock`.

### Windows PowerShell

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Then close and reopen PowerShell, and check that `uv` is available:

```powershell
uv --version
```

If the command is not found, restart the terminal once more or make sure the install location printed by the installer was added to your `PATH`.

### macOS or Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then close and reopen the terminal, and check that `uv` is available:

```bash
uv --version
```

If your shell still cannot find `uv`, follow the PATH message printed by the installer or run the command again in a new terminal session.

Alternative package-manager installs also work, for example `brew install uv` on macOS or `winget install --id=astral-sh.uv -e` on Windows.

## 2. Open the project folder

Download or clone this repository, then open a terminal in the repository root, the folder that contains `pyproject.toml`.

Windows example:

```powershell
cd C:\Users\you\Desktop\pdf_parser
```

macOS or Linux example:

```bash
cd ~/Desktop/pdf_parser
```

## 3. Install dependencies

Run this once after downloading the project:

```bash
uv sync
```

This creates a local `.venv` folder and installs the parser dependencies. You do not need to activate the virtual environment manually when using `uv run`.

## 4. Parse a PDF

You can use any PDF path. Wrap paths in quotes when they contain spaces.

Windows PowerShell:

```powershell
uv run parse-menu "pdf_menu\espn_bet.pdf" --output "output\menu.json"
```

macOS or Linux:

```bash
uv run parse-menu "pdf_menu/espn_bet.pdf" --output "output/menu.json"
```

After the command finishes, open:

- `output/menu.json` for parsed menu items
- `output/menu_structure.json` for detected category structure

The command prints how many menu items were written.

## Useful options

Use a custom structure output path:

```bash
uv run parse-menu "path/to/menu.pdf" --output "output/menu.json" --structure-output "output/categories.json"
```

Use the selected profile's manually listed categories instead of auto-detected categories:

```bash
uv run parse-menu "path/to/menu.pdf" --output "output/menu.json" --profile espn_bet --profile-categories
```

Choose a profile explicitly:

```bash
uv run parse-menu "path/to/menu.pdf" --output "output/menu.json" --profile espn_bet
```

See all CLI options:

```bash
uv run parse-menu --help
```

## Run tests

```bash
uv run pytest
```

The test suite includes unit tests plus smoke tests against `pdf_menu/espn_bet.pdf` when that sample file is present.

## Troubleshooting

`uv` is not recognized:

Close and reopen the terminal. If that does not help, verify that the directory printed by the `uv` installer is in your `PATH`.

Dependency install fails:

Make sure you are in the folder with `pyproject.toml`, then rerun `uv sync`. If your network blocks package downloads, try again on an unrestricted network.

The parser writes zero or very few items:

Make sure the PDF contains selectable text. If you cannot select or copy text from the PDF in a normal PDF viewer, it is probably scanned and needs OCR before this parser can read it.

The categories look wrong:

The default mode detects menu headings from layout signals. For a known layout, try `--profile espn_bet --profile-categories`. For a new layout, add or adjust a `MenuProfile` in `pdf_parser/profiles.py`.

## How it works

The parser is intentionally heuristic. It uses `pdfplumber` word coordinates, splits each page into visual columns, reconstructs lines, detects category headings, then groups item names, prices, and descriptions.

Profiles are used for layout thresholds, filters, and optional manually listed categories. To support a similar machine-generated menu with a known special layout, add a new `MenuProfile` in `pdf_parser/profiles.py` and run the CLI with `--profile`. Add `--profile-categories` only when you want to bypass auto-detected category names.

This project does not perform OCR.
