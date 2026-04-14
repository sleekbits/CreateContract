/* localStorage persistence only */
(function () {
  const KEYS = {
    contracts: "cg_contracts_v1",
    templates: "cg_templates_v1",
    settings: "cg_settings_v1",
    selected: "cg_selected_contract_v1"
  };

  const read = (key, fallback) => {
    try {
      const raw = localStorage.getItem(key);
      return raw ? JSON.parse(raw) : fallback;
    } catch {
      return fallback;
    }
  };

  const write = (key, value) => localStorage.setItem(key, JSON.stringify(value));

  window.StorageAPI = {
    keys: KEYS,
    getContracts: () => read(KEYS.contracts, []),
    saveContracts: (items) => write(KEYS.contracts, items),
    getTemplates: () => read(KEYS.templates, []),
    saveTemplates: (items) => write(KEYS.templates, items),
    getSettings: () => read(KEYS.settings, { currentTemplateId: "tpl-default" }),
    saveSettings: (v) => write(KEYS.settings, v),
    getSelectedContractId: () => read(KEYS.selected, null),
    setSelectedContractId: (id) => write(KEYS.selected, id),
    exportAll: () => ({
      exportedAt: new Date().toISOString(),
      contracts: read(KEYS.contracts, []),
      templates: read(KEYS.templates, []),
      settings: read(KEYS.settings, { currentTemplateId: "tpl-default" })
    }),
    importAll: (payload) => {
      if (!payload || !Array.isArray(payload.contracts) || !Array.isArray(payload.templates)) {
        throw new Error("Invalid backup format");
      }
      write(KEYS.contracts, payload.contracts);
      write(KEYS.templates, payload.templates);
      write(KEYS.settings, payload.settings || { currentTemplateId: "tpl-default" });
    }
  };
})();
