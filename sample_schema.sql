-- SQLite schema used by the desktop app
CREATE TABLE templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_name TEXT NOT NULL UNIQUE,
    template_type TEXT NOT NULL,
    file_path TEXT NOT NULL,
    logo_path TEXT,
    mapping_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE contracts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER,
    contract_title TEXT NOT NULL,
    contract_no TEXT NOT NULL UNIQUE,
    contract_date TEXT NOT NULL,
    client_name TEXT NOT NULL,
    client_address TEXT,
    contractor_name TEXT NOT NULL,
    contractor_address TEXT,
    start_date TEXT,
    end_date TEXT,
    contract_value TEXT,
    scope_of_work TEXT,
    payment_terms TEXT,
    special_conditions TEXT,
    prepared_by TEXT,
    approved_by TEXT,
    status TEXT NOT NULL,
    generated_docx TEXT,
    generated_pdf TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(template_id) REFERENCES templates(id)
);

CREATE TABLE history_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id INTEGER,
    date_created TEXT NOT NULL,
    last_updated TEXT NOT NULL,
    generated_file_name TEXT,
    status TEXT,
    FOREIGN KEY(contract_id) REFERENCES contracts(id)
);

CREATE TABLE audit_trail (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id INTEGER,
    action TEXT NOT NULL,
    details TEXT,
    timestamp TEXT NOT NULL,
    FOREIGN KEY(contract_id) REFERENCES contracts(id)
);
