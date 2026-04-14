/* Offline template definitions (pure HTML placeholders) */
window.TEMPLATE_FIELDS = [
  "contract_title", "contract_no", "contract_date", "client_name", "client_address",
  "contractor_name", "contractor_address", "start_date", "end_date", "contract_value",
  "scope_of_work", "payment_terms", "special_conditions", "prepared_by", "approved_by", "status"
];

window.DEFAULT_TEMPLATE_HTML = `
<h1 style="text-align:center; margin-bottom:8px;">{{contract_title}}</h1>
<p><strong>Contract No:</strong> {{contract_no}}<br/><strong>Date:</strong> {{contract_date}}</p>
<hr/>
<h3>Parties</h3>
<p><strong>Client:</strong> {{client_name}}<br/>{{client_address}}</p>
<p><strong>Contractor:</strong> {{contractor_name}}<br/>{{contractor_address}}</p>
<h3>Duration</h3>
<p><strong>Start Date:</strong> {{start_date}}<br/><strong>End Date:</strong> {{end_date}}</p>
<h3>Commercial Terms</h3>
<p><strong>Contract Value:</strong> {{contract_value}}<br/><strong>Status:</strong> {{status}}</p>
<h3>Scope of Work</h3>
<p style="white-space:pre-wrap;">{{scope_of_work}}</p>
<h3>Payment Terms</h3>
<p style="white-space:pre-wrap;">{{payment_terms}}</p>
<h3>Special Conditions</h3>
<p style="white-space:pre-wrap;">{{special_conditions}}</p>
<br/><br/>
<table style="width:100%; margin-top:32px;"><tr><td><strong>Prepared By</strong><br/>{{prepared_by}}</td><td style="text-align:right;"><strong>Approved By</strong><br/>{{approved_by}}</td></tr></table>
`;

window.DEFAULT_TEMPLATE = {
  id: "tpl-default",
  name: "Standard Service Contract",
  type: "General",
  html: window.DEFAULT_TEMPLATE_HTML,
  mapping: Object.fromEntries(window.TEMPLATE_FIELDS.map((f) => [f, f])),
  docxMeta: null,
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
};
