(function () {
  const REQUIRED = ["contract_no", "contract_title", "contract_date", "client_name", "contractor_name"];

  const uuid = () => `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
  const nowIso = () => new Date().toISOString();

  const formatCurrency = (value) => {
    const n = Number(String(value).replace(/[,\s]/g, ""));
    if (Number.isNaN(n)) return value;
    return n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  };

  const autoContractNo = (contracts) => {
    const y = new Date().getFullYear();
    const prefix = `CNT-${y}-`;
    const seq = contracts.filter((c) => c.contract_no?.startsWith(prefix)).length + 1;
    return `${prefix}${String(seq).padStart(4, "0")}`;
  };

  const validateContract = (data) => {
    const missing = REQUIRED.filter((k) => !String(data[k] || "").trim());
    return { ok: missing.length === 0, missing };
  };

  const renderTemplate = (templateHtml, mapping, data) => {
    return templateHtml.replace(/\{\{\s*([\w_]+)\s*\}\}/g, (_, placeholder) => {
      const field = mapping?.[placeholder] || placeholder;
      return escapeHtml(String(data[field] ?? ""));
    });
  };

  const escapeHtml = (unsafe) => unsafe
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;")
    .replaceAll("\n", "<br/>");

  const downloadText = (filename, text, mime) => {
    const blob = new Blob([text], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const toCsv = (records) => {
    const cols = ["id", "record_id", "contract_no", "contract_title", "contract_date", "client_name", "contractor_name", "status", "created_at", "updated_at"];
    const row = (v) => `"${String(v ?? "").replaceAll('"', '""')}"`;
    return [cols.join(","), ...records.map((r) => cols.map((c) => row(r[c])).join(","))].join("\n");
  };

  window.Utils = { uuid, nowIso, formatCurrency, autoContractNo, validateContract, renderTemplate, downloadText, toCsv };
})();
