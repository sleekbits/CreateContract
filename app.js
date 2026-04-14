(function () {
  let contracts = StorageAPI.getContracts();
  let templates = StorageAPI.getTemplates();
  let settings = StorageAPI.getSettings();
  let editingId = StorageAPI.getSelectedContractId();
  let editingTemplateId = null;

  if (!templates.length) {
    templates = [window.DEFAULT_TEMPLATE];
    StorageAPI.saveTemplates(templates);
  }

  const pageTitle = document.getElementById("pageTitle");
  const toast = document.getElementById("toast");
  const previewDocument = document.getElementById("previewDocument");

  const inputIds = [
    "contract_title", "contract_no", "contract_date", "client_name", "client_address", "contractor_name", "contractor_address",
    "start_date", "end_date", "contract_value", "scope_of_work", "payment_terms", "special_conditions", "prepared_by", "approved_by", "status"
  ];

  const byId = (id) => document.getElementById(id);

  const showToast = (msg, isError = false) => {
    toast.textContent = msg;
    toast.classList.remove("hidden", "error");
    if (isError) toast.classList.add("error");
    setTimeout(() => toast.classList.add("hidden"), 2200);
  };

  const switchPage = (pageId, title) => {
    document.querySelectorAll(".page").forEach((p) => p.classList.remove("active"));
    byId(pageId).classList.add("active");
    document.querySelectorAll(".sidebar button").forEach((b) => b.classList.remove("active"));
    document.querySelector(`.sidebar button[data-page="${pageId}"]`)?.classList.add("active");
    pageTitle.textContent = title;
    if (pageId === "dashboard") renderDashboard();
    if (pageId === "saved-records") renderRecords(byId("searchInput").value);
    if (pageId === "contract-preview") refreshPreview();
  };

  const getCurrentTemplate = () => templates.find((t) => t.id === byId("templateId").value) || templates[0];

  const collectForm = () => {
    const data = Object.fromEntries(inputIds.map((id) => [id, byId(id).value.trim()]));
    data.template_id = byId("templateId").value;
    return data;
  };

  const fillForm = (record) => {
    inputIds.forEach((id) => { byId(id).value = record[id] || ""; });
    byId("templateId").value = record.template_id || templates[0].id;
    editingId = record.id;
    StorageAPI.setSelectedContractId(editingId);
  };

  const resetForm = () => {
    byId("contractForm").reset();
    byId("templateId").value = settings.currentTemplateId || templates[0].id;
    byId("contract_no").value = Utils.autoContractNo(contracts);
    byId("contract_date").valueAsDate = new Date();
    byId("status").value = "Draft";
    editingId = null;
    StorageAPI.setSelectedContractId(null);
  };

  const saveContracts = () => {
    StorageAPI.saveContracts(contracts);
    renderRecords(byId("searchInput").value);
    renderDashboard();
  };

  const saveRecord = (isUpdate = false) => {
    const data = collectForm();
    data.contract_value = Utils.formatCurrency(data.contract_value);
    byId("contract_value").value = data.contract_value;

    const validation = Utils.validateContract(data);
    if (!validation.ok) {
      showToast(`Missing required: ${validation.missing.join(", ")}`, true);
      return;
    }

    if (isUpdate && !editingId) {
      showToast("Select a record first from Saved Records", true);
      return;
    }

    const now = Utils.nowIso();
    if (isUpdate) {
      const idx = contracts.findIndex((c) => c.id === editingId);
      if (idx < 0) return showToast("Record not found", true);
      contracts[idx] = { ...contracts[idx], ...data, updated_at: now };
      showToast("Record updated");
    } else {
      const id = Utils.uuid();
      const record = {
        id,
        record_id: `REC-${id.split("-")[0]}`,
        ...data,
        created_at: now,
        updated_at: now
      };
      contracts.unshift(record);
      editingId = id;
      StorageAPI.setSelectedContractId(id);
      showToast("Record saved");
    }
    saveContracts();
    refreshPreview();
  };

  const deleteSelected = () => {
    const checked = [...document.querySelectorAll(".record-check:checked")].map((i) => i.value);
    if (!checked.length) return showToast("No record selected", true);
    contracts = contracts.filter((c) => !checked.includes(c.id));
    saveContracts();
    showToast(`Deleted ${checked.length} record(s)`);
    if (checked.includes(editingId)) resetForm();
  };

  const duplicateCurrent = () => {
    const data = collectForm();
    const validation = Utils.validateContract(data);
    if (!validation.ok) return showToast("Fill required fields before duplicate", true);
    const id = Utils.uuid();
    contracts.unshift({
      id,
      record_id: `REC-${id.split("-")[0]}`,
      ...data,
      contract_no: Utils.autoContractNo(contracts),
      created_at: Utils.nowIso(),
      updated_at: Utils.nowIso(),
    });
    saveContracts();
    renderRecords("");
    showToast("Duplicated record created");
  };

  const renderRecords = (term = "") => {
    const q = term.trim().toLowerCase();
    const tbody = document.querySelector("#recordsTable tbody");
    tbody.innerHTML = "";

    contracts
      .filter((c) => !q || [c.contract_no, c.contract_title, c.client_name, c.contractor_name, c.contract_date, c.status].some((v) => String(v || "").toLowerCase().includes(q)))
      .forEach((r) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td><input type="checkbox" class="record-check" value="${r.id}"/></td>
          <td>${r.record_id}</td>
          <td><button class="linkish" data-id="${r.id}">${r.contract_no}</button></td>
          <td>${r.contract_title || ""}</td>
          <td>${r.client_name || ""}</td>
          <td>${r.contractor_name || ""}</td>
          <td>${r.contract_date || ""}</td>
          <td>${r.status || ""}</td>
          <td>${new Date(r.updated_at).toLocaleString()}</td>`;
        tbody.appendChild(tr);
      });

    tbody.querySelectorAll("button[data-id]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const rec = contracts.find((c) => c.id === btn.dataset.id);
        if (!rec) return;
        fillForm(rec);
        switchPage("new-contract", "Edit Contract");
      });
    });
  };

  const refreshPreview = () => {
    const tpl = getCurrentTemplate();
    if (!tpl) return;
    const data = collectForm();
    const html = Utils.renderTemplate(tpl.html, tpl.mapping, data);
    previewDocument.innerHTML = html;
  };

  const renderDashboard = () => {
    const cards = byId("dashboardCards");
    const summary = {
      "Total Contracts": contracts.length,
      "Draft": contracts.filter((c) => c.status === "Draft").length,
      "Final": contracts.filter((c) => c.status === "Final").length,
      "Cancelled": contracts.filter((c) => c.status === "Cancelled").length,
      "Expired": contracts.filter((c) => c.status === "Expired").length,
      "Templates": templates.length,
    };
    cards.innerHTML = Object.entries(summary)
      .map(([k, v]) => `<article class="card"><h3>${k}</h3><strong>${v}</strong></article>`)
      .join("");
  };

  const renderTemplateSelect = () => {
    const sel = byId("templateId");
    sel.innerHTML = templates.map((t) => `<option value="${t.id}">${t.type} - ${t.name}</option>`).join("");
    sel.value = settings.currentTemplateId && templates.some((t) => t.id === settings.currentTemplateId)
      ? settings.currentTemplateId
      : templates[0].id;
  };

  const loadTemplateEditor = (templateId) => {
    const tpl = templates.find((t) => t.id === templateId) || templates[0];
    editingTemplateId = tpl.id;
    byId("tpl_name").value = tpl.name;
    byId("tpl_type").value = tpl.type;
    byId("tpl_html").value = tpl.html;
    byId("tpl_mapping").value = JSON.stringify(tpl.mapping, null, 2);
  };

  const saveTemplate = () => {
    const name = byId("tpl_name").value.trim();
    const type = byId("tpl_type").value.trim();
    const html = byId("tpl_html").value.trim();
    if (!name || !type || !html) return showToast("Template name/type/html required", true);

    let mapping;
    try {
      mapping = JSON.parse(byId("tpl_mapping").value || "{}");
    } catch {
      return showToast("Placeholder mapping must be valid JSON", true);
    }

    const file = byId("tpl_docx").files[0];
    const docxMeta = file ? { name: file.name, size: file.size, type: file.type || "application/vnd.openxmlformats-officedocument.wordprocessingml.document" } : null;

    const now = Utils.nowIso();
    if (editingTemplateId) {
      const i = templates.findIndex((t) => t.id === editingTemplateId);
      templates[i] = { ...templates[i], name, type, html, mapping, docxMeta, updatedAt: now };
    } else {
      templates.push({ id: `tpl-${Utils.uuid()}`, name, type, html, mapping, docxMeta, createdAt: now, updatedAt: now });
    }

    StorageAPI.saveTemplates(templates);
    renderTemplateSelect();
    settings.currentTemplateId = byId("templateId").value;
    StorageAPI.saveSettings(settings);
    showToast("Template saved");
  };

  const exportJson = () => {
    Utils.downloadText(`contract-backup-${Date.now()}.json`, JSON.stringify(StorageAPI.exportAll(), null, 2), "application/json");
    showToast("Backup JSON exported");
  };

  const exportCsv = () => {
    Utils.downloadText(`contracts-${Date.now()}.csv`, Utils.toCsv(contracts), "text/csv;charset=utf-8");
    showToast("CSV exported");
  };

  const exportPreviewHtml = () => {
    refreshPreview();
    const docHtml = `<!doctype html><html><head><meta charset="utf-8"><title>Contract</title><style>body{font-family:Segoe UI,Arial;margin:30px;line-height:1.55;}h1,h2,h3{margin-bottom:8px;}</style></head><body>${previewDocument.innerHTML}</body></html>`;
    Utils.downloadText(`contract-preview-${Date.now()}.html`, docHtml, "text/html;charset=utf-8");
    showToast("Printable HTML exported");
  };

  const restoreBackup = async (file) => {
    const txt = await file.text();
    StorageAPI.importAll(JSON.parse(txt));
    contracts = StorageAPI.getContracts();
    templates = StorageAPI.getTemplates();
    settings = StorageAPI.getSettings();
    renderTemplateSelect();
    renderRecords("");
    renderDashboard();
    loadTemplateEditor(byId("templateId").value);
    showToast("Backup restored successfully");
  };

  document.querySelectorAll("#sidebarNav button").forEach((btn) => {
    btn.addEventListener("click", () => switchPage(btn.dataset.page, btn.textContent.trim()));
  });

  byId("regenNo").addEventListener("click", () => byId("contract_no").value = Utils.autoContractNo(contracts));
  byId("saveBtn").addEventListener("click", () => saveRecord(false));
  byId("updateBtn").addEventListener("click", () => saveRecord(true));
  byId("previewBtn").addEventListener("click", () => { refreshPreview(); switchPage("contract-preview", "Contract Preview"); });
  byId("duplicateBtn").addEventListener("click", duplicateCurrent);
  byId("resetBtn").addEventListener("click", resetForm);
  byId("searchInput").addEventListener("input", (e) => renderRecords(e.target.value));
  byId("deleteBtn").addEventListener("click", deleteSelected);
  byId("exportCsvBtn").addEventListener("click", exportCsv);

  byId("templateId").addEventListener("change", (e) => {
    settings.currentTemplateId = e.target.value;
    StorageAPI.saveSettings(settings);
    loadTemplateEditor(e.target.value);
    refreshPreview();
  });

  byId("newTemplateBtn").addEventListener("click", () => {
    editingTemplateId = null;
    byId("tpl_name").value = "";
    byId("tpl_type").value = "";
    byId("tpl_html").value = window.DEFAULT_TEMPLATE_HTML;
    byId("tpl_mapping").value = JSON.stringify(Object.fromEntries(window.TEMPLATE_FIELDS.map((f) => [f, f])), null, 2);
    byId("tpl_docx").value = "";
  });

  byId("saveTemplateBtn").addEventListener("click", saveTemplate);
  byId("refreshPreviewBtn").addEventListener("click", refreshPreview);
  byId("printPreviewBtn").addEventListener("click", () => { switchPage("contract-preview", "Contract Preview"); window.print(); });
  byId("printBtn").addEventListener("click", () => { switchPage("contract-preview", "Contract Preview"); window.print(); });
  byId("exportJsonBtn").addEventListener("click", exportJson);
  byId("downloadBackupBtn").addEventListener("click", exportJson);
  byId("exportHtmlBtn").addEventListener("click", exportPreviewHtml);

  byId("restoreFile").addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (!file) return;
    restoreBackup(file).catch((err) => showToast(err.message || "Restore failed", true));
    e.target.value = "";
  });

  byId("contract_value").addEventListener("blur", () => {
    byId("contract_value").value = Utils.formatCurrency(byId("contract_value").value);
  });

  renderTemplateSelect();
  renderDashboard();
  renderRecords("");
  loadTemplateEditor(byId("templateId").value);
  resetForm();

  if (editingId) {
    const rec = contracts.find((c) => c.id === editingId);
    if (rec) fillForm(rec);
  }
})();
