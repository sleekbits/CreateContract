from __future__ import annotations

import json
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk
from tkcalendar import DateEntry

from app.models import PLACEHOLDER_FIELDS, STATUS_OPTIONS
from app.services.database import DatabaseService
from app.services.sample_assets import ensure_sample_template
from app.services.template_engine import TemplateEngine


class ContractApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Contract Generator (Offline)")
        self.geometry("1320x820")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.db = DatabaseService()
        self.settings = self.db.get_settings()
        self.engine = TemplateEngine(self.settings["default_output_dir"] or "output")
        self.current_contract_id: int | None = None

        self._build_layout()
        self._load_templates()
        self.refresh_dashboard()
        self.refresh_records()

    def _build_layout(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=230, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsw")
        self.sidebar.grid_rowconfigure(8, weight=1)

        ctk.CTkLabel(self.sidebar, text="Contract Suite", font=("Segoe UI", 20, "bold")).grid(
            row=0, column=0, padx=20, pady=(20, 12)
        )

        buttons = [
            ("Dashboard", self.show_dashboard),
            ("New Contract", self.show_new_contract),
            ("Edit Contract", self.show_records),
            ("Contract Records", self.show_records),
            ("Template Settings", self.show_templates),
            ("Export / Generate", self.show_generate),
            ("User Settings", self.show_settings),
        ]
        for idx, (label, cmd) in enumerate(buttons, start=1):
            ctk.CTkButton(self.sidebar, text=label, command=cmd).grid(row=idx, column=0, padx=16, pady=6, sticky="ew")

        self.content = ctk.CTkFrame(self)
        self.content.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        self.frames: dict[str, ctk.CTkFrame] = {}
        self._create_dashboard_frame()
        self._create_contract_form_frame()
        self._create_records_frame()
        self._create_template_settings_frame()
        self._create_generate_frame()
        self._create_settings_frame()

        self.show_dashboard()

    def _raise(self, key: str) -> None:
        for frame in self.frames.values():
            frame.grid_forget()
        self.frames[key].grid(row=0, column=0, sticky="nsew")

    def _create_dashboard_frame(self) -> None:
        frame = ctk.CTkFrame(self.content)
        self.frames["dashboard"] = frame
        self.dashboard_label = ctk.CTkLabel(frame, text="", font=("Segoe UI", 24, "bold"))
        self.dashboard_label.pack(padx=20, pady=20, anchor="w")
        self.status_box = ctk.CTkTextbox(frame, height=300)
        self.status_box.pack(fill="both", expand=True, padx=20, pady=20)

    def _create_contract_form_frame(self) -> None:
        frame = ctk.CTkFrame(self.content)
        self.frames["form"] = frame
        frame.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(frame)
        top.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(top, text="Contract Form", font=("Segoe UI", 22, "bold")).pack(side="left", padx=10, pady=10)

        body = ctk.CTkScrollableFrame(frame)
        body.pack(fill="both", expand=True, padx=15, pady=10)
        self.form_vars: dict[str, tk.StringVar] = {}

        def add_entry(label: str, key: str, row: int, width=380):
            ctk.CTkLabel(body, text=label).grid(row=row, column=0, sticky="w", padx=10, pady=6)
            var = tk.StringVar()
            ent = ctk.CTkEntry(body, textvariable=var, width=width)
            ent.grid(row=row, column=1, sticky="w", padx=10, pady=6)
            self.form_vars[key] = var
            return ent

        add_entry("Contract Title*", "contract_title", 0)
        add_entry("Contract No*", "contract_no", 1)

        ctk.CTkLabel(body, text="Contract Date*").grid(row=2, column=0, sticky="w", padx=10, pady=6)
        self.contract_date = DateEntry(body, width=18, date_pattern="yyyy-mm-dd")
        self.contract_date.grid(row=2, column=1, sticky="w", padx=10, pady=6)

        add_entry("Client Name*", "client_name", 3)
        ctk.CTkLabel(body, text="Client Address").grid(row=4, column=0, sticky="nw", padx=10, pady=6)
        self.client_address = ctk.CTkTextbox(body, width=380, height=80)
        self.client_address.grid(row=4, column=1, padx=10, pady=6, sticky="w")

        add_entry("Contractor Name*", "contractor_name", 5)
        ctk.CTkLabel(body, text="Contractor Address").grid(row=6, column=0, sticky="nw", padx=10, pady=6)
        self.contractor_address = ctk.CTkTextbox(body, width=380, height=80)
        self.contractor_address.grid(row=6, column=1, padx=10, pady=6, sticky="w")

        ctk.CTkLabel(body, text="Start Date").grid(row=7, column=0, sticky="w", padx=10, pady=6)
        self.start_date = DateEntry(body, width=18, date_pattern="yyyy-mm-dd")
        self.start_date.grid(row=7, column=1, sticky="w", padx=10, pady=6)

        ctk.CTkLabel(body, text="End Date").grid(row=8, column=0, sticky="w", padx=10, pady=6)
        self.end_date = DateEntry(body, width=18, date_pattern="yyyy-mm-dd")
        self.end_date.grid(row=8, column=1, sticky="w", padx=10, pady=6)

        add_entry("Contract Value", "contract_value", 9)
        self.form_vars["contract_value"].trace_add("write", self._format_currency)

        ctk.CTkLabel(body, text="Scope of Work").grid(row=10, column=0, sticky="nw", padx=10, pady=6)
        self.scope_text = ctk.CTkTextbox(body, width=700, height=120)
        self.scope_text.grid(row=10, column=1, padx=10, pady=6, sticky="w")

        ctk.CTkLabel(body, text="Payment Terms").grid(row=11, column=0, sticky="nw", padx=10, pady=6)
        self.payment_text = ctk.CTkTextbox(body, width=700, height=100)
        self.payment_text.grid(row=11, column=1, padx=10, pady=6, sticky="w")

        ctk.CTkLabel(body, text="Special Conditions").grid(row=12, column=0, sticky="nw", padx=10, pady=6)
        self.special_text = ctk.CTkTextbox(body, width=700, height=100)
        self.special_text.grid(row=12, column=1, padx=10, pady=6, sticky="w")

        add_entry("Prepared By", "prepared_by", 13)
        add_entry("Approved By", "approved_by", 14)

        ctk.CTkLabel(body, text="Status").grid(row=15, column=0, sticky="w", padx=10, pady=6)
        self.status_option = ctk.CTkOptionMenu(body, values=STATUS_OPTIONS)
        self.status_option.set("Draft")
        self.status_option.grid(row=15, column=1, sticky="w", padx=10, pady=6)

        ctk.CTkLabel(body, text="Template Type").grid(row=16, column=0, sticky="w", padx=10, pady=6)
        self.template_dropdown = ctk.CTkOptionMenu(body, values=["Default"])
        self.template_dropdown.grid(row=16, column=1, sticky="w", padx=10, pady=6)

        btns = ctk.CTkFrame(body)
        btns.grid(row=17, column=0, columnspan=2, sticky="ew", pady=15)
        ctk.CTkButton(btns, text="Save", command=self.save_contract).pack(side="left", padx=8)
        ctk.CTkButton(btns, text="Update", command=self.update_contract).pack(side="left", padx=8)
        ctk.CTkButton(btns, text="Preview", command=self.show_preview).pack(side="left", padx=8)
        ctk.CTkButton(btns, text="Generate Word/PDF", command=self.generate_docs).pack(side="left", padx=8)
        ctk.CTkButton(btns, text="Reset", command=self.reset_form).pack(side="left", padx=8)

    def _create_records_frame(self) -> None:
        frame = ctk.CTkFrame(self.content)
        self.frames["records"] = frame

        top = ctk.CTkFrame(frame)
        top.pack(fill="x", padx=12, pady=8)
        self.search_var = tk.StringVar()
        ctk.CTkEntry(top, textvariable=self.search_var, width=400, placeholder_text="Search by no, client, contractor, date, title").pack(
            side="left", padx=8
        )
        ctk.CTkButton(top, text="Search", command=self.refresh_records).pack(side="left", padx=8)
        ctk.CTkButton(top, text="Load Selected for Edit", command=self.load_selected_record).pack(side="left", padx=8)
        ctk.CTkButton(top, text="Export to Excel", command=self.export_excel).pack(side="right", padx=8)

        cols = ["id", "contract_no", "contract_title", "client_name", "contractor_name", "contract_date", "status", "updated_at"]
        self.tree = ttk.Treeview(frame, columns=cols, show="headings", height=22)
        for c in cols:
            self.tree.heading(c, text=c.replace("_", " ").title())
            self.tree.column(c, width=140, stretch=False)
        self.tree.pack(fill="both", expand=True, padx=12, pady=10)

    def _create_template_settings_frame(self) -> None:
        frame = ctk.CTkFrame(self.content)
        self.frames["templates"] = frame

        ctk.CTkLabel(frame, text="Template Settings", font=("Segoe UI", 22, "bold")).pack(anchor="w", padx=15, pady=10)

        form = ctk.CTkFrame(frame)
        form.pack(fill="x", padx=15, pady=10)

        self.tpl_name = tk.StringVar(value="General Service Contract")
        self.tpl_type = tk.StringVar(value="General")
        self.tpl_file = tk.StringVar()
        self.logo_file = tk.StringVar()

        ctk.CTkEntry(form, textvariable=self.tpl_name, width=240, placeholder_text="Template Name").grid(row=0, column=0, padx=8, pady=6)
        ctk.CTkEntry(form, textvariable=self.tpl_type, width=180, placeholder_text="Template Type").grid(row=0, column=1, padx=8, pady=6)
        ctk.CTkEntry(form, textvariable=self.tpl_file, width=380, placeholder_text="Template File (.docx)").grid(row=0, column=2, padx=8, pady=6)
        ctk.CTkButton(form, text="Browse Template", command=self.browse_template).grid(row=0, column=3, padx=8, pady=6)
        ctk.CTkEntry(form, textvariable=self.logo_file, width=260, placeholder_text="Optional Logo").grid(row=1, column=2, padx=8, pady=6)
        ctk.CTkButton(form, text="Browse Logo", command=self.browse_logo).grid(row=1, column=3, padx=8, pady=6)

        self.mapping_boxes: dict[str, ctk.CTkComboBox] = {}
        mapping_area = ctk.CTkScrollableFrame(frame, height=370)
        mapping_area.pack(fill="both", expand=True, padx=15, pady=10)
        for i, ph in enumerate(PLACEHOLDER_FIELDS.keys()):
            ctk.CTkLabel(mapping_area, text=f"{{{{{ph}}}}}").grid(row=i, column=0, sticky="w", padx=6, pady=4)
            combo = ctk.CTkComboBox(mapping_area, values=list(PLACEHOLDER_FIELDS.keys()), width=260)
            combo.set(ph)
            combo.grid(row=i, column=1, sticky="w", padx=6, pady=4)
            self.mapping_boxes[ph] = combo

        ctk.CTkButton(frame, text="Save Template Configuration", command=self.save_template).pack(anchor="e", padx=20, pady=12)

    def _create_generate_frame(self) -> None:
        frame = ctk.CTkFrame(self.content)
        self.frames["generate"] = frame

        ctk.CTkLabel(frame, text="Export / Generate", font=("Segoe UI", 22, "bold")).pack(anchor="w", padx=15, pady=10)
        ctk.CTkButton(frame, text="Preview Data", command=self.show_preview).pack(anchor="w", padx=15, pady=8)
        ctk.CTkButton(frame, text="Generate Word + PDF", command=self.generate_docs).pack(anchor="w", padx=15, pady=8)
        ctk.CTkButton(frame, text="Print Last Generated File", command=self.print_last).pack(anchor="w", padx=15, pady=8)

        self.gen_log = ctk.CTkTextbox(frame)
        self.gen_log.pack(fill="both", expand=True, padx=15, pady=12)

    def _create_settings_frame(self) -> None:
        frame = ctk.CTkFrame(self.content)
        self.frames["settings"] = frame

        ctk.CTkLabel(frame, text="User Settings", font=("Segoe UI", 22, "bold")).pack(anchor="w", padx=15, pady=10)
        form = ctk.CTkFrame(frame)
        form.pack(fill="x", padx=15, pady=10)

        self.output_dir_var = tk.StringVar(value=self.settings["default_output_dir"] or "output")
        self.company_var = tk.StringVar(value=self.settings["company_name"] or "My Company")

        ctk.CTkEntry(form, textvariable=self.output_dir_var, width=380, placeholder_text="Default output dir").grid(row=0, column=0, padx=8, pady=8)
        ctk.CTkButton(form, text="Browse", command=self.browse_output_dir).grid(row=0, column=1, padx=8, pady=8)
        ctk.CTkEntry(form, textvariable=self.company_var, width=380, placeholder_text="Company name").grid(row=1, column=0, padx=8, pady=8)
        ctk.CTkButton(form, text="Save Settings", command=self.save_settings).grid(row=2, column=0, sticky="w", padx=8, pady=8)

        ctk.CTkButton(frame, text="Backup Database", command=self.backup_db).pack(anchor="w", padx=15, pady=8)
        ctk.CTkButton(frame, text="Restore Database", command=self.restore_db).pack(anchor="w", padx=15, pady=8)

    def _format_currency(self, *_):
        raw = self.form_vars["contract_value"].get().replace(",", "").replace("$", "").strip()
        if not raw:
            return
        if raw[-1] in {".", "-"}:
            return
        try:
            val = float(raw)
        except ValueError:
            return
        self.form_vars["contract_value"].set(f"{val:,.2f}")

    def collect_payload(self) -> dict[str, str]:
        return {
            "template_id": self.template_id_map.get(self.template_dropdown.get(), None),
            "contract_title": self.form_vars["contract_title"].get().strip(),
            "contract_no": self.form_vars["contract_no"].get().strip(),
            "contract_date": self.contract_date.get(),
            "client_name": self.form_vars["client_name"].get().strip(),
            "client_address": self.client_address.get("1.0", "end").strip(),
            "contractor_name": self.form_vars["contractor_name"].get().strip(),
            "contractor_address": self.contractor_address.get("1.0", "end").strip(),
            "start_date": self.start_date.get(),
            "end_date": self.end_date.get(),
            "contract_value": self.form_vars["contract_value"].get().strip(),
            "scope_of_work": self.scope_text.get("1.0", "end").strip(),
            "payment_terms": self.payment_text.get("1.0", "end").strip(),
            "special_conditions": self.special_text.get("1.0", "end").strip(),
            "prepared_by": self.form_vars["prepared_by"].get().strip(),
            "approved_by": self.form_vars["approved_by"].get().strip(),
            "status": self.status_option.get(),
            "generated_docx": "",
            "generated_pdf": "",
        }

    def validate_required(self, payload: dict[str, str]) -> bool:
        required = ["contract_title", "contract_no", "contract_date", "client_name", "contractor_name"]
        missing = [k for k in required if not payload.get(k)]
        if missing:
            messagebox.showerror("Validation", f"Required fields missing: {', '.join(missing)}")
            return False
        return True

    def save_contract(self) -> None:
        payload = self.collect_payload()
        if not self.validate_required(payload):
            return
        try:
            cid = self.db.save_contract(payload)
            self.current_contract_id = cid
            messagebox.showinfo("Saved", f"Contract saved. ID #{cid}")
            self.refresh_records()
            self.refresh_dashboard()
        except Exception as ex:
            messagebox.showerror("Save failed", str(ex))

    def update_contract(self) -> None:
        if not self.current_contract_id:
            messagebox.showwarning("No record", "Load a record first from Contract Records")
            return
        payload = self.collect_payload()
        if not self.validate_required(payload):
            return
        try:
            self.db.save_contract(payload, self.current_contract_id)
            messagebox.showinfo("Updated", "Contract updated")
            self.refresh_records()
            self.refresh_dashboard()
        except Exception as ex:
            messagebox.showerror("Update failed", str(ex))

    def generate_docs(self) -> None:
        payload = self.collect_payload()
        if not self.validate_required(payload):
            return

        template_id = payload["template_id"]
        if not template_id:
            messagebox.showerror("Template missing", "Please configure and select a template first.")
            return

        tpl = self.db.get_template(template_id)
        mapping = json.loads(tpl["mapping_json"])
        context = {ph: payload.get(mapping.get(ph, ph), "") for ph in mapping}

        save_dir = filedialog.askdirectory(title="Select output folder") or self.output_dir_var.get()
        base_name = f"{payload['contract_no']}_{payload['contract_title'].replace(' ', '_')[:30]}"

        try:
            docx_path, pdf_path = self.engine.render_contract(tpl["file_path"], context, save_dir, base_name)
            payload["generated_docx"] = docx_path
            payload["generated_pdf"] = pdf_path

            if self.current_contract_id:
                self.db.save_contract(payload, self.current_contract_id)
            else:
                self.current_contract_id = self.db.save_contract(payload)

            self.gen_log.insert("end", f"Generated: {docx_path}\nGenerated: {pdf_path}\n")
            messagebox.showinfo("Success", "Word and PDF generated successfully")
            self.refresh_records()
        except Exception as ex:
            messagebox.showerror("Generate failed", str(ex))

    def show_preview(self) -> None:
        payload = self.collect_payload()
        win = ctk.CTkToplevel(self)
        win.title("Preview")
        win.geometry("700x620")
        txt = ctk.CTkTextbox(win)
        txt.pack(fill="both", expand=True, padx=10, pady=10)
        for k, v in payload.items():
            txt.insert("end", f"{k}:\n{v}\n\n")

    def reset_form(self) -> None:
        self.current_contract_id = None
        self.form_vars["contract_no"].set(self.db.get_next_contract_no())
        for key, var in self.form_vars.items():
            if key != "contract_no":
                var.set("")
        for box in [self.client_address, self.contractor_address, self.scope_text, self.payment_text, self.special_text]:
            box.delete("1.0", "end")
        self.status_option.set("Draft")

    def show_dashboard(self) -> None:
        self._raise("dashboard")
        self.refresh_dashboard()

    def show_new_contract(self) -> None:
        self._raise("form")
        if not self.form_vars.get("contract_no"):
            return
        if not self.form_vars["contract_no"].get().strip():
            self.form_vars["contract_no"].set(self.db.get_next_contract_no())

    def show_records(self) -> None:
        self._raise("records")
        self.refresh_records()

    def show_templates(self) -> None:
        self._raise("templates")

    def show_generate(self) -> None:
        self._raise("generate")

    def show_settings(self) -> None:
        self._raise("settings")

    def refresh_dashboard(self) -> None:
        stats = self.db.get_dashboard_stats()
        self.dashboard_label.configure(text=f"Total Contracts: {stats['total']}")
        self.status_box.delete("1.0", "end")
        for st, count in stats["status_breakdown"].items():
            self.status_box.insert("end", f"{st}: {count}\n")

    def refresh_records(self) -> None:
        rows = self.db.search_contracts(self.search_var.get() if hasattr(self, "search_var") else "")
        if not hasattr(self, "tree"):
            return
        for i in self.tree.get_children():
            self.tree.delete(i)
        for r in rows:
            self.tree.insert("", "end", values=[r[c] for c in ["id", "contract_no", "contract_title", "client_name", "contractor_name", "contract_date", "status", "updated_at"]])

    def load_selected_record(self) -> None:
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        row = self.db.get_contract(int(values[0]))
        self.current_contract_id = row["id"]

        self.show_new_contract()
        for key in self.form_vars:
            if key in row.keys() and key != "contract_no":
                self.form_vars[key].set(row[key] or "")
        self.form_vars["contract_no"].set(row["contract_no"])
        self.contract_date.set_date(row["contract_date"])
        self.start_date.set_date(row["start_date"] or row["contract_date"])
        self.end_date.set_date(row["end_date"] or row["contract_date"])

        self.client_address.delete("1.0", "end")
        self.client_address.insert("1.0", row["client_address"] or "")
        self.contractor_address.delete("1.0", "end")
        self.contractor_address.insert("1.0", row["contractor_address"] or "")
        self.scope_text.delete("1.0", "end")
        self.scope_text.insert("1.0", row["scope_of_work"] or "")
        self.payment_text.delete("1.0", "end")
        self.payment_text.insert("1.0", row["payment_terms"] or "")
        self.special_text.delete("1.0", "end")
        self.special_text.insert("1.0", row["special_conditions"] or "")
        self.status_option.set(row["status"] or "Draft")

    def _load_templates(self) -> None:
        ensure_sample_template()
        if not self.db.get_templates():
            self.db.save_template(
                {
                    "template_name": "Sample Contract",
                    "template_type": "General",
                    "file_path": "assets/templates/sample_contract_template.docx",
                    "mapping_json": {k: k for k in PLACEHOLDER_FIELDS.keys()},
                    "logo_path": "",
                }
            )
        templates = self.db.get_templates()
        names = [f"{t['template_type']} - {t['template_name']}" for t in templates]
        self.template_id_map = {n: t["id"] for n, t in zip(names, templates)}
        if hasattr(self, "template_dropdown"):
            self.template_dropdown.configure(values=names)
            if names:
                self.template_dropdown.set(names[0])

    def browse_template(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("Word", "*.docx")])
        if path:
            self.tpl_file.set(path)

    def browse_logo(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
        if path:
            self.logo_file.set(path)

    def save_template(self) -> None:
        if not self.tpl_file.get().strip():
            messagebox.showerror("Template", "Please pick a template file")
            return
        installed = TemplateEngine.install_template(self.tpl_file.get(), self.tpl_name.get().strip().replace(" ", "_"))
        mapping = {ph: box.get() for ph, box in self.mapping_boxes.items()}
        self.db.save_template(
            {
                "template_name": self.tpl_name.get().strip(),
                "template_type": self.tpl_type.get().strip() or "General",
                "file_path": installed,
                "logo_path": self.logo_file.get().strip(),
                "mapping_json": mapping,
            }
        )
        self._load_templates()
        messagebox.showinfo("Template", "Template configuration saved")

    def export_excel(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if path:
            self.db.export_contracts_to_excel(path)
            messagebox.showinfo("Export", f"Saved: {path}")

    def backup_db(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".db", filetypes=[("SQLite DB", "*.db")])
        if path:
            self.db.backup_database(path)
            messagebox.showinfo("Backup", "Database backup complete")

    def restore_db(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("SQLite DB", "*.db")])
        if path:
            self.db.restore_database(path)
            self.refresh_records()
            self.refresh_dashboard()
            messagebox.showinfo("Restore", "Database restored")

    def browse_output_dir(self) -> None:
        path = filedialog.askdirectory()
        if path:
            self.output_dir_var.set(path)

    def save_settings(self) -> None:
        self.db.save_settings(self.output_dir_var.get().strip(), self.company_var.get().strip(), "light")
        self.engine = TemplateEngine(self.output_dir_var.get().strip())
        messagebox.showinfo("Settings", "Settings saved")

    def print_last(self) -> None:
        payload = self.collect_payload()
        path = payload.get("generated_pdf")
        if not path:
            messagebox.showwarning("Print", "No generated PDF in current payload. Load/update a record first.")
            return

        try:
            import os

            os.startfile(path, "print")  # type: ignore[attr-defined]
            messagebox.showinfo("Print", "Print command sent")
        except Exception as ex:
            messagebox.showerror("Print", str(ex))


def main() -> None:
    Path("output").mkdir(exist_ok=True)
    app = ContractApp()
    app.reset_form()
    app.mainloop()


if __name__ == "__main__":
    main()
