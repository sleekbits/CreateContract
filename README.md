# Offline Browser Contract Generator (No Backend)

A complete **offline**, **portable**, **browser-only** contract generation app that runs by opening `index.html` directly.

## ✅ What this app is

- Pure frontend app using only:
  - `HTML`
  - `CSS`
  - `Vanilla JavaScript`
- No backend, no server, no localhost, no database server, no Python/Node/PHP.
- No internet needed during use.
- No CDN or online APIs.
- Uses browser `localStorage` for all records/templates/settings.

## Run (zero setup)

1. Download/copy the folder anywhere.
2. Double-click `index.html` (or open it in your browser).
3. Start creating and managing contracts offline.

## Modules included

1. Dashboard
2. New Contract Form (and Edit flow)
3. Saved Records
4. Template Settings
5. Contract Preview
6. Export / Print
7. Backup / Restore

## Core capabilities

- Save, edit, update, duplicate, delete contract records (localStorage)
- Search records by contract number/title/client/contractor/date/status
- Auto-generate contract reference number (`CNT-YYYY-####`)
- Required field validation
- Status support: Draft, Final, Cancelled, Expired
- Multi-template support with template type dropdown
- Placeholder mapping support (`{{placeholder}} -> field`)
- Professional print-ready contract preview
- Print/save as PDF via browser print dialog
- Export all records/templates/settings to JSON backup
- Restore from JSON backup
- Export contract list to CSV (Excel-compatible)
- Export printable contract preview as standalone HTML

## Important .docx note (browser-only limitation)

In strict browser-only offline mode without parser libraries/backend, reliable direct editing of uploaded `.docx` content is not practical.

This project implements the practical approach:

- Use professional **HTML contract templates** with placeholders for generation/preview/print.
- Optional `.docx` upload is accepted as metadata/reference in template settings (file name/size/type), so users can track which source Word template the HTML version corresponds to.

## File structure

```text
.
├─ index.html
├─ style.css
├─ app.js
├─ modules.js
├─ templates.js
├─ storage.js
├─ samples/
│  ├─ sample_placeholder_data.json
│  └─ sample_contract_template.html
└─ README.md
```

## Template placeholders

Supported placeholders:

- `{{contract_title}}`
- `{{contract_no}}`
- `{{contract_date}}`
- `{{client_name}}`
- `{{client_address}}`
- `{{contractor_name}}`
- `{{contractor_address}}`
- `{{start_date}}`
- `{{end_date}}`
- `{{contract_value}}`
- `{{scope_of_work}}`
- `{{payment_terms}}`
- `{{special_conditions}}`
- `{{prepared_by}}`
- `{{approved_by}}`
- `{{status}}`

## Data safety note

Because storage is in browser localStorage only, data can be lost if browser storage is cleared.

Use **Backup / Restore** regularly and keep JSON exports safely.
