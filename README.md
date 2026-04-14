# CreateContract - Offline Windows Desktop Contract Generator

A complete offline desktop application for Windows to fill contract data into existing `.docx` templates and generate final `.docx` + `.pdf` documents automatically.

## Features Included

- Fully offline operation (no cloud APIs, no internet requirement during use)
- Desktop GUI with modern light theme and sidebar navigation
- Modules/pages:
  - Dashboard
  - New Contract
  - Edit Contract (from records)
  - Contract Records
  - Template Settings
  - Export / Generate Document
  - User Settings
- Load/replace Microsoft Word template (`.docx`)
- Placeholder mapping configuration
- SQLite local database storage
- Save + edit contracts
- Search/filter by contract number, title, client, contractor, date
- Generate `.docx` and `.pdf`
- Multi-template support + template type dropdown
- Auto contract reference number (`CNT-YYYY-####`)
- Status handling (`Draft`, `Final`, `Cancelled`, `Expired`)
- Contract history log + audit trail tables
- Export records to Excel
- Backup and restore local database
- Long text fields supported
- Required field validation
- Preview window before generation
- Output folder selection + auto-create folders
- Safe duplicate generation (auto suffix `_1`, `_2`, etc.)

## Tech Stack

- Python 3.11+
- `customtkinter` for desktop UI
- SQLite for local storage
- `docxtpl` for placeholder replacement while preserving Word formatting
- `docx2pdf` / `pywin32` for Word to PDF conversion (Windows)

## Project Structure

```text
CreateContract/
├─ app/
│  ├─ main.py
│  ├─ models.py
│  └─ services/
│     ├─ database.py
│     ├─ sample_assets.py
│     └─ template_engine.py
├─ assets/
│  └─ templates/
│     └─ sample_contract_template.docx   (auto-created on first run if missing)
├─ data/
│  └─ contracts.db                        (auto-created)
├─ output/                                (auto-created)
├─ backups/
├─ requirements.txt
├─ sample_schema.sql
├─ sample_placeholder_mapping.json
└─ sample_contract_template_format.md
```

## Quick Start (Local Run)

1. Create and activate virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run app:

```bash
python -m app.main
```

## Using Your Own Template

1. Open **Template Settings**.
2. Click **Browse Template** and select your existing `.docx` template.
3. Configure placeholder mapping (`{{placeholder}}` -> form field).
4. Save template configuration.
5. In **New Contract**, choose template type and fill form.
6. Click **Generate Word/PDF** and choose output folder.

## PDF Generation Notes

- For best PDF conversion on Windows, install Microsoft Word locally.
- The app tries `docx2pdf`, then `win32com` fallback.
- If Word is unavailable, `.docx` is still generated and a clear error is shown for PDF.

## Database Schema and Mapping Samples

- SQLite schema: `sample_schema.sql`
- Placeholder mapping sample: `sample_placeholder_mapping.json`
- Sample template placeholder format: `sample_contract_template_format.md`

## Build Windows EXE (PyInstaller)

```bash
pip install pyinstaller
pyinstaller --noconfirm --windowed --name CreateContract --add-data "assets;assets" --add-data "data;data" app/main.py
```

Executable output:

- `dist/CreateContract/CreateContract.exe`

## Offline/Production Notes

- No internet API calls are used by application logic.
- All data is stored locally in SQLite file (`data/contracts.db`).
- Template, mapping, output files remain on local machine.

