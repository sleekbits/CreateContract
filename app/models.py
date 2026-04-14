from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


PLACEHOLDER_FIELDS: Dict[str, str] = {
    "contract_title": "Contract Title",
    "contract_no": "Contract Number",
    "contract_date": "Contract Date",
    "client_name": "Client Name",
    "client_address": "Client Address",
    "contractor_name": "Contractor Name",
    "contractor_address": "Contractor Address",
    "start_date": "Start Date",
    "end_date": "End Date",
    "contract_value": "Contract Value",
    "scope_of_work": "Scope of Work",
    "payment_terms": "Payment Terms",
    "special_conditions": "Special Conditions",
    "prepared_by": "Prepared By",
    "approved_by": "Approved By",
    "status": "Status",
}

STATUS_OPTIONS: List[str] = ["Draft", "Final", "Cancelled", "Expired"]


@dataclass
class ContractRecord:
    id: int | None
    template_id: int | None
    contract_title: str
    contract_no: str
    contract_date: str
    client_name: str
    client_address: str
    contractor_name: str
    contractor_address: str
    start_date: str
    end_date: str
    contract_value: str
    scope_of_work: str
    payment_terms: str
    special_conditions: str
    prepared_by: str
    approved_by: str
    status: str
    generated_docx: str = ""
    generated_pdf: str = ""
