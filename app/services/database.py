from __future__ import annotations

import json
import shutil
import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path
from typing import Any


class DatabaseService:
    def __init__(self, db_path: str = "data/contracts.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with closing(self._connect()) as conn, conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_name TEXT NOT NULL UNIQUE,
                    template_type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    logo_path TEXT,
                    mapping_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS contracts (
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

                CREATE TABLE IF NOT EXISTS history_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contract_id INTEGER,
                    date_created TEXT NOT NULL,
                    last_updated TEXT NOT NULL,
                    generated_file_name TEXT,
                    status TEXT,
                    FOREIGN KEY(contract_id) REFERENCES contracts(id)
                );

                CREATE TABLE IF NOT EXISTS audit_trail (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contract_id INTEGER,
                    action TEXT NOT NULL,
                    details TEXT,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY(contract_id) REFERENCES contracts(id)
                );

                CREATE TABLE IF NOT EXISTS app_settings (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    default_output_dir TEXT,
                    company_name TEXT,
                    theme TEXT
                );

                INSERT OR IGNORE INTO app_settings (id, default_output_dir, company_name, theme)
                VALUES (1, 'output', 'My Company', 'light');
                """
            )

    def _now(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_next_contract_no(self) -> str:
        year = datetime.now().strftime("%Y")
        with closing(self._connect()) as conn:
            row = conn.execute(
                "SELECT COUNT(*) as c FROM contracts WHERE contract_no LIKE ?", (f"CNT-{year}-%",)
            ).fetchone()
        seq = (row["c"] or 0) + 1
        return f"CNT-{year}-{seq:04d}"

    def save_contract(self, payload: dict[str, Any], contract_id: int | None = None) -> int:
        now = self._now()
        with closing(self._connect()) as conn, conn:
            if contract_id:
                fields = ", ".join([f"{k} = ?" for k in payload])
                values = list(payload.values()) + [now, contract_id]
                conn.execute(f"UPDATE contracts SET {fields}, updated_at = ? WHERE id = ?", values)
                self._insert_history(conn, contract_id, now, payload.get("generated_docx", ""), payload.get("status", "Draft"))
                self._audit(conn, contract_id, "UPDATE", f"Updated contract {payload.get('contract_no', '')}")
                return contract_id

            cols = ", ".join(payload.keys())
            placeholders = ", ".join(["?"] * len(payload))
            values = list(payload.values()) + [now, now]
            conn.execute(
                f"INSERT INTO contracts ({cols}, created_at, updated_at) VALUES ({placeholders}, ?, ?)",
                values,
            )
            new_id = conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
            self._insert_history(conn, new_id, now, payload.get("generated_docx", ""), payload.get("status", "Draft"))
            self._audit(conn, new_id, "CREATE", f"Created contract {payload.get('contract_no', '')}")
            return new_id

    def _insert_history(self, conn: sqlite3.Connection, contract_id: int, ts: str, filename: str, status: str) -> None:
        conn.execute(
            """
            INSERT INTO history_log (contract_id, date_created, last_updated, generated_file_name, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (contract_id, ts, ts, Path(filename).name if filename else "", status),
        )

    def _audit(self, conn: sqlite3.Connection, contract_id: int, action: str, details: str) -> None:
        conn.execute(
            "INSERT INTO audit_trail (contract_id, action, details, timestamp) VALUES (?, ?, ?, ?)",
            (contract_id, action, details, self._now()),
        )

    def get_contract(self, contract_id: int) -> sqlite3.Row | None:
        with closing(self._connect()) as conn:
            return conn.execute("SELECT * FROM contracts WHERE id = ?", (contract_id,)).fetchone()

    def search_contracts(self, query: str = "") -> list[sqlite3.Row]:
        q = f"%{query.strip()}%"
        with closing(self._connect()) as conn:
            return conn.execute(
                """
                SELECT * FROM contracts
                WHERE contract_no LIKE ? OR contractor_name LIKE ? OR client_name LIKE ?
                   OR contract_date LIKE ? OR contract_title LIKE ?
                ORDER BY updated_at DESC
                """,
                (q, q, q, q, q),
            ).fetchall()

    def get_dashboard_stats(self) -> dict[str, Any]:
        with closing(self._connect()) as conn:
            total = conn.execute("SELECT COUNT(*) c FROM contracts").fetchone()["c"]
            by_status = conn.execute("SELECT status, COUNT(*) c FROM contracts GROUP BY status").fetchall()
        return {"total": total, "status_breakdown": {r["status"]: r["c"] for r in by_status}}

    def get_templates(self) -> list[sqlite3.Row]:
        with closing(self._connect()) as conn:
            return conn.execute("SELECT * FROM templates ORDER BY updated_at DESC").fetchall()

    def save_template(self, data: dict[str, Any], template_id: int | None = None) -> int:
        now = self._now()
        with closing(self._connect()) as conn, conn:
            if template_id:
                conn.execute(
                    """
                    UPDATE templates
                    SET template_name=?, template_type=?, file_path=?, logo_path=?, mapping_json=?, updated_at=?
                    WHERE id=?
                    """,
                    (
                        data["template_name"],
                        data["template_type"],
                        data["file_path"],
                        data.get("logo_path", ""),
                        json.dumps(data["mapping_json"]),
                        now,
                        template_id,
                    ),
                )
                return template_id

            conn.execute(
                """
                INSERT INTO templates (template_name, template_type, file_path, logo_path, mapping_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["template_name"],
                    data["template_type"],
                    data["file_path"],
                    data.get("logo_path", ""),
                    json.dumps(data["mapping_json"]),
                    now,
                    now,
                ),
            )
            return conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]

    def get_template(self, template_id: int) -> sqlite3.Row | None:
        with closing(self._connect()) as conn:
            return conn.execute("SELECT * FROM templates WHERE id = ?", (template_id,)).fetchone()

    def export_contracts_to_excel(self, filepath: str) -> None:
        import pandas as pd

        with closing(self._connect()) as conn:
            rows = conn.execute("SELECT * FROM contracts ORDER BY updated_at DESC").fetchall()
        df = pd.DataFrame([dict(r) for r in rows])
        df.to_excel(filepath, index=False)

    def backup_database(self, backup_path: str) -> None:
        Path(backup_path).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(self.db_path, backup_path)

    def restore_database(self, backup_path: str) -> None:
        shutil.copy2(backup_path, self.db_path)

    def get_settings(self) -> sqlite3.Row:
        with closing(self._connect()) as conn:
            return conn.execute("SELECT * FROM app_settings WHERE id = 1").fetchone()

    def save_settings(self, default_output_dir: str, company_name: str, theme: str) -> None:
        with closing(self._connect()) as conn, conn:
            conn.execute(
                "UPDATE app_settings SET default_output_dir=?, company_name=?, theme=? WHERE id=1",
                (default_output_dir, company_name, theme),
            )
