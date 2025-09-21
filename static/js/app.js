/**
 * Symplifika Dashboard Application
 * Gerencia a interface do dashboard e integração com APIs
 */

class SymphilikaApp {
  constructor() {
    this.apiBaseUrl = "/shortcuts/api/";
    this.csrfToken = this.getCSRFToken();
    this.currentUser = null;
    this.categories = [];
    this.shortcuts = [];

    this.init();
  }

  /**
   * Inicializa a aplicação
   */
  init() {
    this.bindEvents();
    this.loadInitialData();
    this.setupFormHandlers();
    this.loadSettings();
  }

  /**
   * Obtém o token CSRF
   */
  getCSRFToken() {
    const token = document.querySelector("[name=csrfmiddlewaretoken]");
    return token ? token.value : "";
  }

  /**
   * Vincula eventos da interface
   */
  bindEvents() {
    // Eventos de formulários
    this.setupShortcutForm();
    this.setupCategoryForm();

    // Eventos de navegação
    this.setupNavigation();
    this.setupSearchAndFilters();

    // Eventos de interface
    document.addEventListener("DOMContentLoaded", () => {
      this.loadRecentShortcuts();
      this.loadDashboardStats();
      this.setupSettingsForm();
      this.setupThemeToggle();
    });
  }

  /**
   * Alterna o tema claro/escuro manualmente
   */
  setupThemeToggle() {
    const themeToggleBtns = document.querySelectorAll("[data-theme-toggle]");
    themeToggleBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        // Alternar classe dark no html
        document.documentElement.classList.toggle("dark");
        // Salvar preferência no localStorage
        if (document.documentElement.classList.contains("dark")) {
          localStorage.setItem("theme", "dark");
        } else {
          localStorage.setItem("theme", "light");
        }
      });
    });

    // Aplicar preferência salva ao carregar
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme === "dark") {
      document.documentElement.classList.add("dark");
    } else if (savedTheme === "light") {
      document.documentElement.classList.remove("dark");
    }
  }

  /**
   * Carrega dados iniciais
   */
  async loadInitialData() {
    try {
      await Promise.all([
        this.loadCategories(),
        this.loadRecentShortcuts(),
        this.loadDashboardStats(),
        this.loadAllShortcuts(),
      ]);
    } catch (error) {
      console.error("Erro ao carregar dados iniciais:", error);
      this.showNotification("Erro ao carregar dados", "error");
    }
  }

  /**
   * Carrega categorias do usuário
   */
  async loadCategories() {
    try {
      const response = await fetch(`${this.apiBaseUrl}categories/`, {
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": this.csrfToken,
        },
      });

      if (!response.ok) {
        throw new Error("Erro ao carregar categorias");
      }

      const data = await response.json();
      this.categories = data.results || data;
      this.updateCategorySelects();
      this.displayAllCategories(this.categories);
    } catch (error) {
      console.error("Erro ao carregar categorias:", error);
    }
  }

  /**
   * Carrega atalhos recentes
   */
  async loadRecentShortcuts() {
    try {
      const response = await fetch(
        `${this.apiBaseUrl}shortcuts/?ordering=-last_used&page_size=5`,
        {
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": this.csrfToken,
          },
        },
      );

      if (!response.ok) {
        throw new Error("Erro ao carregar atalhos recentes");
      }

      const data = await response.json();
      const shortcuts = data.results || data;
      this.displayRecentShortcuts(shortcuts);
    } catch (error) {
      console.error("Erro ao carregar atalhos recentes:", error);
      this.displayRecentShortcutsError();
    }
  }

  /**
   * Carrega estatísticas do dashboard
   */
  async loadDashboardStats() {
    try {
      const response = await fetch(`/api/dashboard/stats/`, {
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": this.csrfToken,
        },
      });

      if (!response.ok) {
        throw new Error("Erro ao carregar estatísticas");
      }

      const stats = await response.json();
      this.updateDashboardStats(stats);
    } catch (error) {
      console.error("Erro ao carregar estatísticas:", error);
    }
  }

  /**
   * Configura manipuladores de formulários
   */
  setupFormHandlers() {
    this.setupShortcutForm();
    this.setupCategoryForm();
  }

  /**
   * Configura o formulário de atalhos
   */
  setupShortcutForm() {
    const form = document.getElementById("createShortcutForm");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      await this.handleShortcutSubmit(form);
    });

    // Configurar eventos de mudança de tipo de expansão
    const expansionTypes = form.querySelectorAll(
      'input[name="expansion_type"]',
    );
    expansionTypes.forEach((radio) => {
      radio.addEventListener("change", () => {
        this.handleExpansionTypeChange();
      });
    });

    // Configurar preview do gatilho
    const triggerInput = form.querySelector("#shortcutTrigger");
    if (triggerInput) {
      triggerInput.addEventListener("input", () => {
        this.updateTriggerPreview();
      });
    }

    // Configurar botão de adicionar variável
    const addVariableBtn = form.querySelector("#addVariableBtn");
    if (addVariableBtn) {
      addVariableBtn.addEventListener("click", () => {
        this.addVariableField();
      });
    }

    // Configurar contador de caracteres para conteúdo
    const contentTextarea = form.querySelector("#shortcutContent");
    if (contentTextarea) {
      contentTextarea.addEventListener("input", () => {
        this.updateCharacterCount(contentTextarea);
      });
    }
  }

  /**
   * Configura o formulário de categorias
   */
  setupCategoryForm() {
    const form = document.getElementById("createCategoryForm");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      await this.handleCategorySubmit(form);
    });

    // Sincronizar cor com campo de texto
    const colorInput = form.querySelector("#categoryColor");
    const colorTextInput = form.querySelector("#categoryColorText");

    if (colorInput && colorTextInput) {
      colorInput.addEventListener("change", () => {
        colorTextInput.value = colorInput.value;
      });

      colorTextInput.addEventListener("input", () => {
        if (/^#[0-9A-F]{6}$/i.test(colorTextInput.value)) {
          colorInput.value = colorTextInput.value;
        }
      });
    }
  }

  /**
   * Manipula envio do formulário de atalho
   */
  async handleShortcutSubmit(form) {
    const submitBtn = form.querySelector("#submitShortcutBtn");
    const loadingIcon = form.querySelector("#submitShortcutLoading");
    const submitText = form.querySelector("#submitShortcutText");

    try {
      // Mostrar loading
      this.setLoadingState(submitBtn, loadingIcon, submitText, true);

      const formData = new FormData(form);
      const data = this.formDataToObject(formData);

      // Processar trigger - adicionar // se não tiver
      if (data.trigger && !data.trigger.startsWith("//")) {
        data.trigger = "//" + data.trigger;
      }

      // Processar categoria - converter para ID se necessário
      if (data.category === "") {
        delete data.category;
      }

      // Garantir que ai_prompt nunca seja nulo
      if (!data.ai_prompt) {
        data.ai_prompt = "";
      }

      // Processar checkbox is_active
      data.is_active =
        form.querySelector('[name="is_active"]')?.checked ?? true;

      // Processar variáveis se tipo dinâmico
      if (data.expansion_type === "dynamic") {
        const variables = this.collectVariables(form);
        if (Object.keys(variables).length > 0) {
          data.variables = variables;
        }
      }

      const shortcutId = data.shortcut_id;
      const isEdit = shortcutId && shortcutId !== "";

      const url = isEdit
        ? `${this.apiBaseUrl}shortcuts/${shortcutId}/`
        : `${this.apiBaseUrl}shortcuts/`;

      const method = isEdit ? "PUT" : "POST";

      const response = await fetch(url, {
        method: method,
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": this.csrfToken,
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json();
        let errorMessage = "Erro ao salvar atalho";

        if (errorData.trigger) {
          errorMessage = Array.isArray(errorData.trigger)
            ? errorData.trigger[0]
            : errorData.trigger;
        } else if (errorData.detail) {
          errorMessage = errorData.detail;
        } else if (errorData.non_field_errors) {
          errorMessage = Array.isArray(errorData.non_field_errors)
            ? errorData.non_field_errors[0]
            : errorData.non_field_errors;
        }

        throw new Error(errorMessage);
      }

      const shortcut = await response.json();

      // Sucesso
      this.showNotification(
        isEdit
          ? "Atalho atualizado com sucesso!"
          : "Atalho criado com sucesso!",
        "success",
      );

      this.closeCreateShortcutModal();
      this.loadRecentShortcuts(); // Recarregar atalhos recentes
      this.loadAllShortcuts(); // Recarregar lista completa

      // Disparar evento customizado
      document.dispatchEvent(
        new CustomEvent("shortcutSaved", {
          detail: { shortcut, isEdit },
        }),
      );
    } catch (error) {
      console.error("Erro ao salvar atalho:", error);
      this.showNotification(error.message || "Erro ao salvar atalho", "error");
    } finally {
      // Remover loading
      this.setLoadingState(submitBtn, loadingIcon, submitText, false);
    }
  }

  /**
   * Manipula envio do formulário de categoria
   */
  async handleCategorySubmit(form) {
    const submitBtn = form.querySelector("#submitCategoryBtn");
    const loadingIcon = form.querySelector("#submitCategoryLoading");
    const submitText = form.querySelector("#submitCategoryText");

    try {
      // Mostrar loading
      this.setLoadingState(submitBtn, loadingIcon, submitText, true);

      const formData = new FormData(form);
      const data = this.formDataToObject(formData);

      // Debug logging
      console.log("[DEBUG] Form data collected:", data);
      console.log("[DEBUG] CSRF Token:", this.csrfToken);

      const categoryId = data.category_id;
      const isEdit = categoryId && categoryId !== "";

      const url = isEdit
        ? `${this.apiBaseUrl}categories/${categoryId}/`
        : `${this.apiBaseUrl}categories/`;

      const method = isEdit ? "PUT" : "POST";

      console.log("[DEBUG] Request URL:", url);
      console.log("[DEBUG] Request method:", method);
      console.log("[DEBUG] Request body:", JSON.stringify(data));

      const response = await fetch(url, {
        method: method,
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": this.csrfToken,
        },
        body: JSON.stringify(data),
      });

      console.log("[DEBUG] Response status:", response.status);
      console.log("[DEBUG] Response headers:", [...response.headers.entries()]);

      if (!response.ok) {
        const errorText = await response.text();
        console.log("[DEBUG] Error response text:", errorText);

        let errorData;
        try {
          errorData = JSON.parse(errorText);
        } catch (e) {
          console.log("[DEBUG] Could not parse error as JSON:", e);
          errorData = { detail: errorText };
        }

        console.log("[DEBUG] Parsed error data:", errorData);

        // Handle field-specific errors
        if (errorData.name && Array.isArray(errorData.name)) {
          throw new Error(errorData.name[0]);
        }
        if (errorData.color && Array.isArray(errorData.color)) {
          throw new Error(errorData.color[0]);
        }
        if (errorData.description && Array.isArray(errorData.description)) {
          throw new Error(errorData.description[0]);
        }

        throw new Error(
          errorData.detail ||
            errorData.message ||
            errorData.non_field_errors?.[0] ||
            "Erro ao salvar categoria",
        );
      }

      const category = await response.json();

      // Sucesso
      this.showNotification(
        isEdit
          ? "Categoria atualizada com sucesso!"
          : "Categoria criada com sucesso!",
        "success",
      );

      this.closeCreateCategoryModal();
      await this.loadCategories(); // Recarregar categorias

      // Disparar evento customizado
      document.dispatchEvent(
        new CustomEvent("categorySaved", {
          detail: { category, isEdit },
        }),
      );
    } catch (error) {
      console.error("Erro ao salvar categoria:", error);

      // Show user-friendly error message
      let errorMessage = "Erro ao salvar categoria";

      if (error.message.includes("Já existe uma categoria")) {
        errorMessage =
          "Já existe uma categoria com este nome. Escolha um nome diferente.";
      } else if (error.message.includes("nome da categoria é obrigatório")) {
        errorMessage = "O nome da categoria é obrigatório.";
      } else if (error.message.includes("pelo menos 2 caracteres")) {
        errorMessage = "O nome da categoria deve ter pelo menos 2 caracteres.";
      } else if (error.message.includes("máximo 100 caracteres")) {
        errorMessage = "O nome da categoria deve ter no máximo 100 caracteres.";
      } else if (error.message.includes("formato hexadecimal")) {
        errorMessage = "A cor deve estar no formato hexadecimal (#RRGGBB).";
      } else if (error.message) {
        errorMessage = error.message;
      }

      this.showNotification(errorMessage, "error");
    } finally {
      // Remover loading
      this.setLoadingState(submitBtn, loadingIcon, submitText, false);
    }
  }

  /**
   * Converte FormData para objeto
   */
  formDataToObject(formData) {
    const obj = {};
    for (let [key, value] of formData.entries()) {
      if (key !== "csrfmiddlewaretoken") {
        // Converter valores vazios para null
        obj[key] = value === "" ? null : value;
      }
    }
    return obj;
  }

  /**
   * Coleta variáveis do formulário dinâmico
   */
  collectVariables(form) {
    const variables = {};
    const variableFields = form.querySelectorAll(".variable-field");

    variableFields.forEach((field) => {
      const keyInput = field.querySelector('[name="variable_key"]');
      const valueInput = field.querySelector('[name="variable_value"]');

      if (
        keyInput &&
        valueInput &&
        keyInput.value.trim() &&
        valueInput.value.trim()
      ) {
        variables[keyInput.value.trim()] = valueInput.value.trim();
      }
    });

    return variables;
  }

  /**
   * Define estado de loading dos botões
   */
  setLoadingState(button, loadingIcon, textSpan, isLoading) {
    if (isLoading) {
      button.disabled = true;
      loadingIcon?.classList.remove("hidden");
      if (textSpan) textSpan.textContent = "Salvando...";
    } else {
      button.disabled = false;
      loadingIcon?.classList.add("hidden");
      if (textSpan) {
        const isEdit = button
          .closest("form")
          .querySelector('[name="shortcut_id"], [name="category_id"]')?.value;
        textSpan.textContent = isEdit ? "Atualizar" : "Criar";
      }
    }
  }

  /**
   * Abre modal de criação de atalho
   */
  openCreateShortcutModal(shortcut = null) {
    const modal = document.getElementById("createShortcutModal");
    const form = document.getElementById("createShortcutForm");

    if (!modal || !form) return;

    // Reset do formulário
    form.reset();

    if (shortcut) {
      // Modo de edição
      this.populateShortcutForm(shortcut);
      document.getElementById("shortcutModalTitle").textContent =
        "Editar Atalho";
      document.getElementById("submitShortcutText").textContent =
        "Atualizar Atalho";
    } else {
      // Modo de criação
      document.getElementById("shortcutModalTitle").textContent =
        "Criar Novo Atalho";
      document.getElementById("submitShortcutText").textContent =
        "Criar Atalho";
    }

    // Abrir modal
    if (window.Symplifika && window.Symplifika.Modal) {
      window.Symplifika.Modal.open("createShortcutModal");
    } else {
      modal.classList.remove("hidden");
    }
  }

  /**
   * Abre modal de criação de categoria
   */
  openCreateCategoryModal(category = null) {
    const modal = document.getElementById("createCategoryModal");
    const form = document.getElementById("createCategoryForm");

    if (!modal || !form) return;

    // Reset do formulário
    form.reset();

    if (category) {
      // Modo de edição
      this.populateCategoryForm(category);
      document.getElementById("categoryModalTitle").textContent =
        "Editar Categoria";
      document.getElementById("submitCategoryText").textContent =
        "Atualizar Categoria";
    } else {
      // Modo de criação
      document.getElementById("categoryModalTitle").textContent =
        "Nova Categoria";
      document.getElementById("submitCategoryText").textContent =
        "Criar Categoria";
    }

    // Abrir modal
    if (window.Symplifika && window.Symplifika.Modal) {
      window.Symplifika.Modal.open("createCategoryModal");
    } else {
      modal.classList.remove("hidden");
    }
  }

  /**
   * Fecha modal de criação de atalho
   */
  closeCreateShortcutModal() {
    if (window.Symplifika && window.Symplifika.Modal) {
      window.Symplifika.Modal.close("createShortcutModal");
    } else {
      const modal = document.getElementById("createShortcutModal");
      if (modal) modal.classList.add("hidden");
    }
  }

  /**
   * Fecha modal de criação de categoria
   */
  closeCreateCategoryModal() {
    if (window.Symplifika && window.Symplifika.Modal) {
      window.Symplifika.Modal.close("createCategoryModal");
    } else {
      const modal = document.getElementById("createCategoryModal");
      if (modal) modal.classList.add("hidden");
    }
  }

  /**
   * Popula formulário de atalho para edição
   */
  populateShortcutForm(shortcut) {
    const form = document.getElementById("createShortcutForm");
    if (!form) return;

    // Preencher campos
    const fields = [
      "shortcut_id",
      "trigger",
      "title",
      "content",
      "category",
      "expansion_type",
      "ai_prompt",
    ];
    fields.forEach((field) => {
      const input = form.querySelector(`[name="${field}"], #${field}`);
      if (input && shortcut[field] !== undefined) {
        let value = shortcut[field];

        // Processar trigger - remover // do início para exibição
        if (field === "trigger" && value && value.startsWith("//")) {
          value = value.substring(2);
        }

        if (input.type === "radio") {
          const radio = form.querySelector(
            `[name="${field}"][value="${value}"]`,
          );
          if (radio) radio.checked = true;
        } else if (input.type === "checkbox") {
          input.checked = Boolean(value);
        } else {
          input.value = value || "";
        }
      }
    });

    // Preencher variáveis se existirem
    if (shortcut.variables) {
      this.populateVariables(form, shortcut.variables);
    }
  }

  /**
   * Popula variáveis no formulário
   */
  populateVariables(form, variables) {
    const variablesList = form.querySelector("#variablesList");
    if (!variablesList) return;

    // Limpar variáveis existentes
    variablesList.innerHTML = "";

    // Adicionar cada variável
    Object.entries(variables).forEach(([key, value]) => {
      this.addVariableField(key, value);
    });
  }

  /**
   * Adiciona campo de variável
   */
  addVariableField(key = "", value = "") {
    const variablesList = document.getElementById("variablesList");
    if (!variablesList) return;

    const variableDiv = document.createElement("div");
    variableDiv.className = "flex space-x-2 items-center variable-field";

    variableDiv.innerHTML = `
      <input type="text" placeholder="nome_variavel" value="${this.escapeHtml(key)}"
             class="flex-1 form-input text-sm" name="variable_key">
      <span class="text-gray-400">=</span>
      <input type="text" placeholder="Valor padrão" value="${this.escapeHtml(value)}"
             class="flex-1 form-input text-sm" name="variable_value">
      <button type="button" onclick="this.parentElement.remove()"
              class="text-red-500 hover:text-red-700 p-1">
        <svg class="w-4 h-4" fill="none" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>
    `;

    variablesList.appendChild(variableDiv);
  }

  /**
   * Popula formulário de categoria para edição
   */
  populateCategoryForm(category) {
    const form = document.getElementById("createCategoryForm");
    if (!form) return;

    // Preencher campos
    const fields = ["category_id", "name", "description", "color"];
    fields.forEach((field) => {
      const input = form.querySelector(`[name="${field}"], #${field}`);
      if (input && category[field] !== undefined) {
        input.value = category[field];
      }
    });

    // Atualizar campo de cor
    const colorText = form.querySelector("#categoryColorText");
    if (colorText && category.color) {
      colorText.value = category.color;
    }
  }

  /**
   * Atualiza selects de categoria
   */
  updateCategorySelects() {
    const selects = document.querySelectorAll('select[name="category"]');

    selects.forEach((select) => {
      // Limpar opções existentes (exceto a primeira)
      const firstOption = select.querySelector('option[value=""]');
      select.innerHTML = "";
      if (firstOption) {
        select.appendChild(firstOption.cloneNode(true));
      }

      // Adicionar categorias
      this.categories.forEach((category) => {
        const option = document.createElement("option");
        option.value = category.id;
        option.textContent = category.name;
        select.appendChild(option);
      });
    });
  }

  /**
   * Exibe atalhos recentes na interface
   */
  displayRecentShortcuts(shortcuts) {
    const container = document.getElementById("recentShortcuts");
    if (!container) return;

    if (shortcuts.length === 0) {
      container.innerHTML = `
                <div class="flex items-center justify-center py-8 text-gray-500 dark:text-gray-400">
                    <span>Nenhum atalho encontrado</span>
                </div>
            `;
      return;
    }

    container.innerHTML = shortcuts
      .map(
        (shortcut) => `
            <div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-gray-900 dark:text-white truncate">
                        ${this.escapeHtml(shortcut.title)}
                    </p>
                    <p class="text-xs text-gray-500 dark:text-gray-400">
                        //${this.escapeHtml(shortcut.trigger)}
                    </p>
                </div>
                <div class="flex items-center space-x-2">
                    <span class="text-xs text-gray-500 dark:text-gray-400">
                        ${shortcut.use_count || 0} usos
                    </span>
                    <div class="flex items-center space-x-1">
                        <button
                            onclick="window.app.editShortcut(${shortcut.id})"
                            class="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 p-1 rounded transition-colors"
                            title="Editar atalho"
                        >
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                            </svg>
                        </button>
                        <button
                            onclick="window.app.deleteShortcut(${shortcut.id})"
                            class="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300 p-1 rounded transition-colors"
                            title="Excluir atalho"
                        >
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                            </svg>
                        </button>
                        <button
                            onclick="window.app.useShortcut(${shortcut.id})"
                            class="text-symplifika-primary hover:text-symplifika-primary-dark p-1 rounded transition-colors"
                            title="Usar atalho"
                        >
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        `,
      )
      .join("");
  }

  /**
   * Carrega todos os atalhos do usuário
   */
  async loadAllShortcuts() {
    try {
      console.log("Chamando loadAllShortcuts");
      const response = await fetch(`${this.apiBaseUrl}shortcuts/`, {
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": this.csrfToken,
        },
      });

      if (!response.ok) {
        throw new Error("Erro ao carregar atalhos");
      }

      const data = await response.json();
      this.shortcuts = data.results || data;
      console.log("Atalhos carregados:", this.shortcuts);
      this.displayAllShortcuts(this.shortcuts);
    } catch (error) {
      console.error("Erro ao carregar atalhos:", error);
      this.displayShortcutsError();
    }
  }

  /**
   * Exibe todos os atalhos na página de atalhos
   */
  displayAllShortcuts(shortcuts) {
    console.log("Chamando displayAllShortcuts com:", shortcuts);
    const container = document.getElementById("shortcutsList");
    const loadingEl = document.getElementById("loadingShortcuts");
    const emptyEl = document.getElementById("emptyShortcuts");

    if (!container) {
      console.warn("Container #shortcutsList não encontrado!");
      return;
    }

    // Esconder loading
    if (loadingEl) loadingEl.classList.add("hidden");

    if (shortcuts.length === 0) {
      if (emptyEl) emptyEl.classList.remove("hidden");
      return;
    }

    // Esconder empty state
    if (emptyEl) emptyEl.classList.add("hidden");

    container.innerHTML = shortcuts
      .map(
        (shortcut) => `
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4 sm:p-6 border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow flex flex-col h-full">
            <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2 sm:gap-4 mb-4">
              <div class="flex-1 min-w-0">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-1 break-words">
                  ${this.escapeHtml(shortcut.title || "")}
                </h3>
                <p class="text-sm text-gray-500 dark:text-gray-400 mb-2 truncate">
                  ${this.escapeHtml(shortcut.trigger || "")}
                </p>
                ${
                  shortcut.category
                    ? `
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-${shortcut.category.color || "gray"}-100 text-${shortcut.category.color || "gray"}-800 dark:bg-${shortcut.category.color || "gray"}-900 dark:text-${shortcut.category.color || "gray"}-200">
                    ${this.escapeHtml(shortcut.category?.name || "")}
                  </span>
                `
                    : ""
                }
              </div>
              <div class="flex flex-row flex-wrap items-center gap-2 sm:flex-col sm:items-end sm:gap-2 ml-0 sm:ml-4">
                <button
                  onclick="window.app.editShortcut(${shortcut.id})"
                  class="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 p-2 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors"
                  title="Editar atalho"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                  </svg>
                </button>
                <button
                  onclick="window.app.deleteShortcut(${shortcut.id})"
                  class="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300 p-2 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                  title="Excluir atalho"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                  </svg>
                </button>
                <button
                  onclick="window.app.useShortcut(${shortcut.id})"
                  class="text-symplifika-primary hover:text-symplifika-primary-dark p-2 rounded-lg hover:bg-symplifika-primary/10 transition-colors"
                  title="Usar atalho"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                  </svg>
                </button>
              </div>
            </div>

            <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-3 mb-4 flex-1">
              <p class="text-sm text-gray-600 dark:text-gray-300 break-words line-clamp-3">
                ${this.escapeHtml(shortcut.content || "")}
              </p>
            </div>

            <div class="flex flex-col sm:flex-row sm:items-center justify-between text-sm text-gray-500 dark:text-gray-400 gap-2">
              <div class="flex flex-row flex-wrap items-center gap-4">
                <span class="flex items-center">
                  <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/>
                  </svg>
                  ${shortcut.use_count || 0} usos
                </span>
                <span class="flex items-center">
                  <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                  ${shortcut.last_used ? new Date(shortcut.last_used).toLocaleDateString() : "Nunca usado"}
                </span>
              </div>
              <div class="flex flex-row flex-wrap items-center gap-2">
                ${shortcut.expansion_type === "ai_enhanced" ? '<span class="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded text-xs">IA</span>' : ""}
                ${shortcut.expansion_type === "dynamic" ? '<span class="px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded text-xs">Dinâmico</span>' : ""}
                ${shortcut.is_active ? '<span class="px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded text-xs">Ativo</span>' : '<span class="px-2 py-1 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 rounded text-xs">Inativo</span>'}
              </div>
            </div>
          </div>
        `,
      )
      .join("");
  }

  /**
   * Exibe erro ao carregar atalhos
   */
  displayShortcutsError() {
    const container = document.getElementById("shortcutsList");
    const loadingEl = document.getElementById("loadingShortcuts");

    if (loadingEl) loadingEl.classList.add("hidden");

    if (container) {
      container.innerHTML = `
        <div class="col-span-full flex flex-col items-center justify-center py-12">
          <svg class="w-16 h-16 text-red-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <h3 class="text-xl font-semibold text-gray-600 dark:text-gray-400 mb-2">
            Erro ao carregar atalhos
          </h3>
          <p class="text-gray-500 dark:text-gray-500 mb-6">
            Ocorreu um erro ao carregar seus atalhos. Tente novamente.
          </p>
          <button onclick="window.app.loadAllShortcuts()" class="btn btn-primary">
            Tentar Novamente
          </button>
        </div>
      `;
    }
  }

  /**
   * Exibe erro ao carregar atalhos recentes
   */
  displayRecentShortcutsError() {
    const container = document.getElementById("recentShortcuts");
    if (!container) return;

    container.innerHTML = `
            <div class="flex items-center justify-center py-8 text-red-500 dark:text-red-400">
                <span>Erro ao carregar atalhos recentes</span>
            </div>
        `;
  }

  /**
   * Atualiza estatísticas do dashboard
   */
  updateDashboardStats(stats) {
    // Atualizar cards rápidos
    const totalShortcuts = document.getElementById("dashboardTotalShortcuts");
    const todayUsages = document.getElementById("dashboardTodayUsages");
    const totalCategories = document.getElementById("dashboardTotalCategories");
    const totalUsages = document.getElementById("dashboardTotalUsages");

    if (totalShortcuts) totalShortcuts.textContent = stats.total_shortcuts || 0;
    if (todayUsages) todayUsages.textContent = stats.usages_today || 0;
    if (totalCategories)
      totalCategories.textContent = stats.total_categories || 0;
    if (totalUsages) totalUsages.textContent = stats.total_usages || 0;

    // --- Gráfico de atividades dos últimos 7 dias ---
    if (window.dashboardWeeklyChartInstance) {
      window.dashboardWeeklyChartInstance.destroy();
    }
    const weeklyUsage = stats.weekly_usage || [];
    const weeklyLabels = weeklyUsage.map(
      (item) => item.day || item.label || "",
    );
    const weeklyData = weeklyUsage.map((item) => item.count || 0);

    const dashboardWeeklyChartCtx = document.getElementById(
      "dashboardWeeklyChart",
    );
    if (dashboardWeeklyChartCtx && typeof Chart !== "undefined") {
      window.dashboardWeeklyChartInstance = new Chart(dashboardWeeklyChartCtx, {
        type: "bar",
        data: {
          labels: weeklyLabels,
          datasets: [
            {
              label: "Usos",
              data: weeklyData,
              backgroundColor: "#2563eb",
              borderRadius: 6,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
          },
          scales: {
            x: { grid: { display: false } },
            y: { beginAtZero: true, grid: { color: "#e5e7eb" } },
          },
        },
      });
    }
  }

  /**
   * Usa um atalho
   */
  async useShortcut(shortcutId, context = "") {
    try {
      const response = await fetch(
        `${this.apiBaseUrl}shortcuts/${shortcutId}/use/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": this.csrfToken,
          },
          body: JSON.stringify({ context }),
        },
      );

      if (!response.ok) {
        throw new Error("Erro ao usar atalho");
      }

      const result = await response.json();

      // Copiar conteúdo para clipboard
      await navigator.clipboard.writeText(result.content);

      this.showNotification(
        "Atalho copiado para a área de transferência!",
        "success",
      );

      // Recarregar atalhos recentes
      this.loadRecentShortcuts();
    } catch (error) {
      console.error("Erro ao usar atalho:", error);
      this.showNotification("Erro ao usar atalho", "error");
    }
  }

  /**
   * Manipula mudança no tipo de expansão
   */
  handleExpansionTypeChange() {
    const form = document.getElementById("createShortcutForm");
    if (!form) return;

    const selectedType = form.querySelector(
      'input[name="expansion_type"]:checked',
    )?.value;

    // Gerenciar seções baseadas no tipo
    const aiPromptSection = form.querySelector("#aiPromptSection");
    const variablesSection = form.querySelector("#variablesSection");
    const contentHelp = form.querySelector("#contentHelp");

    // Esconder todas as seções primeiro
    if (aiPromptSection) aiPromptSection.classList.add("hidden");
    if (variablesSection) variablesSection.classList.add("hidden");

    // Remover required de todos os campos opcionais
    const aiPromptTextarea = form.querySelector("#aiPrompt");
    if (aiPromptTextarea) aiPromptTextarea.required = false;

    // Atualizar estilo dos labels
    form.querySelectorAll(".expansion-type-label").forEach((label) => {
      label.classList.remove(
        "border-blue-500",
        "bg-blue-50",
        "dark:bg-blue-900/20",
      );
      label.classList.add("border-gray-200", "dark:border-gray-600");
    });

    const selectedLabel = form.querySelector(
      `label[for="type_${selectedType}"]`,
    );
    if (selectedLabel) {
      selectedLabel.classList.remove("border-gray-200", "dark:border-gray-600");
      selectedLabel.classList.add(
        "border-blue-500",
        "bg-blue-50",
        "dark:bg-blue-900/20",
      );
    }

    // Mostrar seções relevantes baseadas no tipo
    switch (selectedType) {
      case "ai_enhanced":
        if (aiPromptSection) {
          aiPromptSection.classList.remove("hidden");
          if (aiPromptTextarea) aiPromptTextarea.required = true;
        }
        if (contentHelp) {
          contentHelp.textContent =
            "Digite o texto base que será expandido pela IA";
        }
        break;
      case "dynamic":
        if (variablesSection) {
          variablesSection.classList.remove("hidden");
        }
        if (contentHelp) {
          contentHelp.textContent =
            "Use {nome_da_variavel} para criar campos substituíveis";
        }
        break;
      default: // static
        if (contentHelp) {
          contentHelp.textContent =
            "Digite o texto que será inserido quando usar o atalho";
        }
    }
  }

  /**
   * Atualiza contador de caracteres
   */
  updateCharacterCount(textarea) {
    const charCount = document.getElementById("charCount");
    if (charCount && textarea) {
      const count = textarea.value.length;
      charCount.textContent = `${count} caracteres`;

      // Adicionar indicação visual para textos muito longos
      if (count > 1000) {
        charCount.className = "text-xs text-orange-500";
      } else if (count > 2000) {
        charCount.className = "text-xs text-red-500";
      } else {
        charCount.className = "text-xs text-gray-400";
      }
    }
  }

  /**
   * Atualiza preview do gatilho
   */
  updateTriggerPreview() {
    const input = document.getElementById("shortcutTrigger");
    const preview = document.getElementById("triggerPreview");

    if (input && preview) {
      const value = input.value.trim();
      preview.textContent = `//${value || "seu-atalho"}`;

      // Validação visual do gatilho
      if (value.length > 0) {
        // Verificar caracteres válidos
        const validPattern = /^[a-zA-Z0-9\-_]+$/;
        if (!validPattern.test(value)) {
          input.classList.add("border-red-500");
          this.showFieldError(
            input,
            "Use apenas letras, números, hífens e underscores",
          );
        } else if (value.length < 2) {
          input.classList.add("border-orange-500");
          this.showFieldError(input, "Mínimo de 2 caracteres");
        } else {
          input.classList.remove("border-red-500", "border-orange-500");
          this.clearFieldError(input);
        }
      }
    }
  }

  /**
   * Mostra erro em campo
   */
  showFieldError(input, message) {
    this.clearFieldError(input);

    const errorDiv = document.createElement("div");
    errorDiv.className = "field-error text-red-500 text-xs mt-1";
    errorDiv.textContent = message;

    input.parentElement.appendChild(errorDiv);
  }

  /**
   * Limpa erro de campo
   */
  clearFieldError(input) {
    const existingError = input.parentElement.querySelector(".field-error");
    if (existingError) {
      existingError.remove();
    }
  }

  /**
   * Mostra página específica (implementação futura)
   */
  showPage(page) {
    console.log("Showing page:", page);
    // Implementar navegação entre páginas se necessário
  }

  /**
   * Exporta atalhos (implementação futura)
   */
  exportShortcuts() {
    console.log("Exporting shortcuts...");
    // Implementar exportação
  }

  /**
   * Importa atalhos (implementação futura)
   */
  importShortcuts() {
    console.log("Importing shortcuts...");
    // Implementar importação
  }

  /**
   * Limpa todos os dados (implementação futura)
   */
  clearAllData() {
    console.log("Clearing all data...");
    // Implementar limpeza de dados
  }

  /**
   * Exibe notificação
   */
  showNotification(message, type = "info") {
    // Implementar sistema de notificações
    console.log(`[${type.toUpperCase()}] ${message}`);

    // Usar toast personalizado se disponível
    this.showToast(message, type);
  }

  /**
   * Abre modal para editar atalho
   */
  async editShortcut(shortcutId) {
    try {
      // Carregar dados do atalho
      const response = await fetch(
        `${this.apiBaseUrl}shortcuts/${shortcutId}/`,
        {
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": this.csrfToken,
          },
        },
      );

      if (!response.ok) {
        throw new Error("Erro ao carregar dados do atalho");
      }

      const shortcut = await response.json();

      // Abrir modal de criação em modo edição
      this.openCreateShortcutModal(shortcut);
    } catch (error) {
      console.error("Erro ao editar atalho:", error);
      this.showNotification("Erro ao carregar atalho para edição", "error");
    }
  }

  /**
   * Exclui um atalho
   */
  async deleteShortcut(shortcutId) {
    this.showConfirmationModal(
      "Excluir Atalho",
      "Tem certeza que deseja excluir este atalho? Esta ação não pode ser desfeita.",
      "Excluir",
      async () => {
        try {
          const response = await fetch(
            `${this.apiBaseUrl}shortcuts/${shortcutId}/`,
            {
              method: "DELETE",
              headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": this.csrfToken,
              },
            },
          );

          if (!response.ok) {
            throw new Error("Erro ao excluir atalho");
          }

          this.showToast("Atalho excluído com sucesso!", "success");

          // Recarregar atalhos recentes e lista completa
          this.loadRecentShortcuts();
          this.loadAllShortcuts();

          // Disparar evento customizado
          document.dispatchEvent(
            new CustomEvent("shortcutDeleted", {
              detail: { shortcutId },
            }),
          );
        } catch (error) {
          console.error("Erro ao excluir atalho:", error);
          this.showToast("Erro ao excluir atalho", "error");
        }
      },
    );
  }

  /**
   * Abre modal de upgrade
   */
  showUpgradeModal() {
    // Verificar se já existe um modal de upgrade
    let modal = document.getElementById("upgradeModal");

    if (!modal) {
      // Criar modal de upgrade
      modal = document.createElement("div");
      modal.id = "upgradeModal";
      modal.className =
        "modal fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 hidden";

      modal.innerHTML = `
           <div class="modal-content bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
             <div class="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
               <h3 class="text-xl font-semibold text-gray-900 dark:text-white">
                 Planos Premium
               </h3>
               <button
                 type="button"
                 onclick="window.app.closeUpgradeModal()"
                 class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
               >
                 <svg class="w-6 h-6" fill="none" stroke="currentColor">
                   <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                 </svg>
               </button>
             </div>

             <div class="p-6">
               <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                 <!-- Plano Premium -->
                 <div class="bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg p-6 border border-blue-200 dark:border-blue-700">
                   <div class="text-center mb-4">
                     <h4 class="text-xl font-bold text-gray-900 dark:text-white">Premium</h4>
                     <p class="text-3xl font-bold text-blue-600 dark:text-blue-400 mt-2">R$ 19<span class="text-lg">/mês</span></p>
                   </div>
                   <ul class="space-y-3 text-sm text-gray-600 dark:text-gray-300">
                     <li class="flex items-center">
                       <svg class="w-4 h-4 text-green-500 mr-2" fill="none" stroke="currentColor">
                         <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                       </svg>
                       500 atalhos
                     </li>
                     <li class="flex items-center">
                       <svg class="w-4 h-4 text-green-500 mr-2" fill="none" stroke="currentColor">
                         <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                       </svg>
                       1.000 expansões IA/mês
                     </li>
                     <li class="flex items-center">
                       <svg class="w-4 h-4 text-green-500 mr-2" fill="none" stroke="currentColor">
                         <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                       </svg>
                       Estatísticas avançadas
                     </li>
                     <li class="flex items-center">
                       <svg class="w-4 h-4 text-green-500 mr-2" fill="none" stroke="currentColor">
                         <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                       </svg>
                       Suporte prioritário
                     </li>
                   </ul>
                   <button class="w-full mt-6 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors">
                     Escolher Premium
                   </button>
                 </div>

                 <!-- Plano Enterprise -->
                 <div class="bg-gradient-to-br from-purple-50 to-pink-100 dark:from-purple-900/20 dark:to-pink-900/20 rounded-lg p-6 border border-purple-200 dark:border-purple-700 relative">
                   <div class="absolute -top-3 left-1/2 transform -translate-x-1/2">
                     <span class="bg-purple-600 text-white text-xs px-3 py-1 rounded-full">Mais Popular</span>
                   </div>
                   <div class="text-center mb-4">
                     <h4 class="text-xl font-bold text-gray-900 dark:text-white">Enterprise</h4>
                     <p class="text-3xl font-bold text-purple-600 dark:text-purple-400 mt-2">R$ 49<span class="text-lg">/mês</span></p>
                   </div>
                   <ul class="space-y-3 text-sm text-gray-600 dark:text-gray-300">
                     <li class="flex items-center">
                       <svg class="w-4 h-4 text-green-500 mr-2" fill="none" stroke="currentColor">
                         <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                       </svg>
                       Atalhos ilimitados
                     </li>
                     <li class="flex items-center">
                       <svg class="w-4 h-4 text-green-500 mr-2" fill="none" stroke="currentColor">
                         <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                       </svg>
                       10.000 expansões IA/mês
                     </li>
                     <li class="flex items-center">
                       <svg class="w-4 h-4 text-green-500 mr-2" fill="none" stroke="currentColor">
                         <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                       </svg>
                       API personalizada
                     </li>
                     <li class="flex items-center">
                       <svg class="w-4 h-4 text-green-500 mr-2" fill="none" stroke="currentColor">
                         <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                       </svg>
                       Suporte dedicado
                     </li>
                   </ul>
                   <button class="w-full mt-6 bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-4 rounded-lg transition-colors">
                     Escolher Enterprise
                   </button>
                 </div>
               </div>

               <div class="text-center mt-8 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                 <p class="text-sm text-gray-600 dark:text-gray-300">
                   🔒 Pagamento seguro • 💸 7 dias grátis • ❌ Cancele quando quiser
                 </p>
               </div>
             </div>
           </div>
         `;

      document.body.appendChild(modal);
    }

    // Mostrar modal
    modal.classList.remove("hidden");
    document.body.style.overflow = "hidden";
  }

  /**
   * Fecha modal de upgrade
   */
  closeUpgradeModal() {
    const modal = document.getElementById("upgradeModal");
    if (modal) {
      modal.classList.add("hidden");
      document.body.style.overflow = "";
    }
  }

  /**
   * Atualiza estatísticas de uso de IA
   */
  updateAIUsageStats(used, max) {
    const usageBar = document.getElementById("aiUsageBar");
    const usageText = document.getElementById("aiUsageText");

    if (usageBar && usageText) {
      const percentage = Math.min((used / max) * 100, 100);
      usageBar.style.width = `${percentage}%`;
      usageText.textContent = `${used}/${max}`;

      // Alterar cor da barra baseado no uso
      usageBar.className = usageBar.className.replace(/bg-\w+-\d+/g, "");
      if (percentage >= 90) {
        usageBar.classList.add("bg-red-500");
      } else if (percentage >= 70) {
        usageBar.classList.add("bg-yellow-500");
      } else {
        usageBar.classList.add("bg-symplifika-primary");
      }
    }
  }

  /**
   * Configura eventos globais
   */
  setupGlobalEvents() {
    // Configurar botões de export/import
    const exportBtn = document.getElementById("exportShortcutsBtn");
    if (exportBtn) {
      exportBtn.addEventListener("click", () => this.exportShortcuts());
    }

    const importBtn = document.getElementById("importShortcutsBtn");
    if (importBtn) {
      importBtn.addEventListener("click", () => this.importShortcuts());
    }
  }

  /**
   * Sistema de navegação entre páginas
   */
  setupNavigation() {
    // Adicionar event listeners para itens de navegação
    const navItems = document.querySelectorAll("[data-page]");
    navItems.forEach((item) => {
      item.addEventListener("click", (e) => {
        e.preventDefault();
        const page = item.getAttribute("data-page");
        this.showPage(page);

        // Se a aba selecionada for "Atalhos", carregar os atalhos
        if (page === "shortcuts") {
          this.loadAllShortcuts();
        }
        // Se a aba selecionada for "Categorias", carregar as categorias
        if (page === "categories") {
          this.loadCategories();
        }

        // Atualizar estado ativo
        navItems.forEach((nav) => nav.classList.remove("active"));
        item.classList.add("active");
      });
    });
  }

  /**
   * Exibe uma página específica
   */
  showPage(pageName) {
    // Esconder todas as páginas
    const pages = document.querySelectorAll(".page");
    pages.forEach((page) => page.classList.add("hidden"));

    // Mostrar página específica
    const targetPage = document.getElementById(`${pageName}Page`);
    if (targetPage) {
      targetPage.classList.remove("hidden");

      // Carregar dados específicos da página
      this.loadPageData(pageName);
    }
  }

  /**
   * Carrega dados específicos de cada página
   */
  loadPageData(pageName) {
    switch (pageName) {
      case "shortcuts":
        this.loadAllShortcuts();
        break;
      case "categories":
        this.loadCategories();
        break;
      case "statistics":
        this.loadStatistics();
        break;
      case "dashboard":
        this.loadDashboardStats();
        this.loadRecentShortcuts();
        break;
    }
  }

  /**
   * Configurar pesquisa e filtros
   */
  setupSearchAndFilters() {
    // Pesquisa de atalhos
    const searchInput = document.getElementById("searchInput");
    if (searchInput) {
      let searchTimeout;
      searchInput.addEventListener("input", (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
          this.searchShortcuts(e.target.value);
        }, 300);
      });
    }

    // Filtro de categoria
    const categoryFilter = document.getElementById("categoryFilter");
    if (categoryFilter) {
      categoryFilter.addEventListener("change", (e) => {
        this.filterShortcutsByCategory(e.target.value);
      });
    }

    // Botões de criar
    const createShortcutBtns = document.querySelectorAll(
      "#createShortcutBtn, .create-shortcut-btn",
    );
    createShortcutBtns.forEach((btn) => {
      btn.addEventListener("click", () => this.openCreateShortcutModal());
    });

    const createCategoryBtn = document.getElementById("createCategoryBtn");
    if (createCategoryBtn) {
      createCategoryBtn.addEventListener("click", () =>
        this.openCreateCategoryModal(),
      );
    }

    // Atalhos de teclado
    document.addEventListener("keydown", (e) => {
      if (e.ctrlKey || e.metaKey) {
        switch (e.key.toLowerCase()) {
          case "n":
            e.preventDefault();
            this.openCreateShortcutModal();
            break;
          case "f":
            e.preventDefault();
            if (searchInput) searchInput.focus();
            break;
          case "/":
            e.preventDefault();
            if (searchInput) searchInput.focus();
            break;
        }
      }
    });
  }

  /**
   * Pesquisa atalhos
   */
  searchShortcuts(query) {
    const filteredShortcuts = this.shortcuts.filter(
      (shortcut) =>
        shortcut.title.toLowerCase().includes(query.toLowerCase()) ||
        shortcut.trigger.toLowerCase().includes(query.toLowerCase()) ||
        shortcut.content.toLowerCase().includes(query.toLowerCase()),
    );
    this.displayAllShortcuts(filteredShortcuts);
  }

  /**
   * Filtra atalhos por categoria
   */
  filterShortcutsByCategory(categoryId) {
    let filteredShortcuts = this.shortcuts;

    if (categoryId && categoryId !== "") {
      filteredShortcuts = this.shortcuts.filter(
        (shortcut) =>
          shortcut.category && shortcut.category.id.toString() === categoryId,
      );
    }

    this.displayAllShortcuts(filteredShortcuts);
  }

  /**
   * Carrega estatísticas
   */
  async loadStatistics() {
    try {
      const response = await fetch(`${this.apiBaseUrl}shortcuts/stats/`, {
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": this.csrfToken,
        },
      });

      if (!response.ok) {
        throw new Error("Erro ao carregar estatísticas");
      }

      const stats = await response.json();
      this.displayStatistics(stats);
    } catch (error) {
      console.error("Erro ao carregar estatísticas:", error);
    }
  }

  /**
   * Exibe estatísticas
   */
  displayStatistics(stats) {
    // Atualizar elementos de estatísticas na página
    const elements = {
      totalShortcuts: document.getElementById("statsTotalShortcuts"),
      totalUsages: document.getElementById("statsTotalUsages"),
      totalCategories: document.getElementById("statsTotalCategories"),
      timeSaved: document.getElementById("statsTimeSaved"),
      activeShortcuts: document.getElementById("statsActiveShortcuts"),
      usagesToday: document.getElementById("statsUsagesToday"),
    };

    if (elements.totalShortcuts) {
      elements.totalShortcuts.textContent = stats.total_shortcuts || 0;
    }
    if (elements.totalUsages) {
      elements.totalUsages.textContent = stats.total_usages || 0;
    }
    if (elements.totalCategories) {
      elements.totalCategories.textContent = stats.total_categories || 0;
    }
    if (elements.timeSaved) {
      const hours = Math.floor((stats.time_saved || 0) / 3600);
      elements.timeSaved.textContent = hours + "h";
    }
    if (elements.activeShortcuts) {
      elements.activeShortcuts.textContent = stats.active_shortcuts || 0;
    }
    if (elements.usagesToday) {
      elements.usagesToday.textContent = stats.usages_today || 0;
    }

    // Atualizar lista de top atalhos
    this.displayTopShortcuts(stats.top_shortcuts || []);

    // Atualizar atividade recente
    this.displayRecentActivity(stats.recent_activity || []);

    // --- Gráficos ---
    // Uso semanal
    if (window.weeklyChartInstance) {
      window.weeklyChartInstance.destroy();
    }
    const weeklyUsage = stats.weekly_usage || [];
    const weeklyLabels = weeklyUsage.map(
      (item) => item.day || item.label || "",
    );
    const weeklyData = weeklyUsage.map((item) => item.count || 0);

    const weeklyChartCtx = document.getElementById("weeklyChart");
    if (weeklyChartCtx && typeof Chart !== "undefined") {
      window.weeklyChartInstance = new Chart(weeklyChartCtx, {
        type: "bar",
        data: {
          labels: weeklyLabels,
          datasets: [
            {
              label: "Usos",
              data: weeklyData,
              backgroundColor: "#2563eb",
              borderRadius: 6,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: false },
          },
          scales: {
            x: { grid: { display: false } },
            y: { beginAtZero: true, grid: { color: "#e5e7eb" } },
          },
        },
      });
    }

    // Distribuição por categoria
    if (window.categoryChartInstance) {
      window.categoryChartInstance.destroy();
    }
    const categoryDist = stats.category_distribution || [];
    const categoryLabels = categoryDist.map(
      (item) => item.category || item.label || "",
    );
    const categoryData = categoryDist.map((item) => item.count || 0);

    const categoryChartCtx = document.getElementById("categoryChart");
    if (categoryChartCtx && typeof Chart !== "undefined") {
      window.categoryChartInstance = new Chart(categoryChartCtx, {
        type: "doughnut",
        data: {
          labels: categoryLabels,
          datasets: [
            {
              data: categoryData,
              backgroundColor: [
                "#2563eb",
                "#22c55e",
                "#f59e42",
                "#a855f7",
                "#f43f5e",
                "#14b8a6",
                "#eab308",
              ],
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: "bottom" },
          },
        },
      });
    }
  }

  /**
   * Exibe top atalhos
   */
  displayTopShortcuts(topShortcuts) {
    const container = document.getElementById("topShortcutsList");
    if (!container) return;

    if (topShortcuts.length === 0) {
      container.innerHTML = `
        <div class="text-center py-8 text-gray-500 dark:text-gray-400">
          <span>Nenhum atalho usado ainda</span>
        </div>
      `;
      return;
    }

    container.innerHTML = topShortcuts
      .slice(0, 5)
      .map(
        (shortcut, index) => `
        <div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
          <div class="flex items-center space-x-3">
            <div class="flex-shrink-0">
              <span class="inline-flex items-center justify-center w-6 h-6 rounded-full bg-symplifika-primary text-white text-xs font-bold">
                ${index + 1}
              </span>
            </div>
            <div>
              <p class="text-sm font-medium text-gray-900 dark:text-white">
                ${this.escapeHtml(shortcut.title)}
              </p>
              <p class="text-xs text-gray-500 dark:text-gray-400">
                ${this.escapeHtml(shortcut.trigger)}
              </p>
            </div>
          </div>
          <div class="text-right">
            <p class="text-sm font-semibold text-gray-900 dark:text-white">
              ${shortcut.use_count || 0}
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-400">usos</p>
          </div>
        </div>
      `,
      )
      .join("");
  }

  /**
   * Exibe atividade recente
   */
  displayRecentActivity(recentActivity) {
    const container = document.getElementById("recentActivityList");
    if (!container) return;

    if (recentActivity.length === 0) {
      container.innerHTML = `
        <div class="text-center py-8 text-gray-500 dark:text-gray-400">
          <span>Nenhuma atividade recente</span>
        </div>
      `;
      return;
    }

    container.innerHTML = recentActivity
      .slice(0, 5)
      .map(
        (activity) => `
        <div class="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
          <div class="flex-shrink-0">
            <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
            </svg>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm text-gray-900 dark:text-white">
              Usou <strong>${this.escapeHtml(activity.shortcut_title)}</strong>
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-400">
              ${this.formatRelativeTime(activity.used_at)}
            </p>
          </div>
        </div>
      `,
      )
      .join("");
  }

  /**
   * Formata tempo relativo
   */
  formatRelativeTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMs = now - date;
    const diffInMinutes = Math.floor(diffInMs / (1000 * 60));
    const diffInHours = Math.floor(diffInMinutes / 60);
    const diffInDays = Math.floor(diffInHours / 24);

    if (diffInMinutes < 1) return "agora mesmo";
    if (diffInMinutes < 60) return `${diffInMinutes}min atrás`;
    if (diffInHours < 24) return `${diffInHours}h atrás`;
    if (diffInDays === 1) return "ontem";
    if (diffInDays < 7) return `${diffInDays} dias atrás`;

    return date.toLocaleDateString();
  }

  /**
   * Exibe modal de confirmação personalizado
   */
  showConfirmationModal(title, message, confirmText, onConfirm) {
    const modal = document.getElementById("confirmationModal");
    const titleEl = document.getElementById("confirmationTitle");
    const messageEl = document.getElementById("confirmationMessage");
    const confirmBtn = document.getElementById("confirmationConfirm");
    const confirmTextEl = document.getElementById("confirmationConfirmText");

    if (!modal || !titleEl || !messageEl || !confirmBtn || !confirmTextEl) {
      // Fallback para alert nativo se modal não estiver disponível
      if (confirm(message)) {
        onConfirm();
      }
      return;
    }

    titleEl.textContent = title;
    messageEl.textContent = message;
    confirmTextEl.textContent = confirmText;

    // Limpar event listeners anteriores
    const newConfirmBtn = confirmBtn.cloneNode(true);
    confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);

    // Adicionar novo event listener
    newConfirmBtn.addEventListener("click", async () => {
      const loadingIcon = document.getElementById("confirmationConfirmLoading");

      // Mostrar loading
      if (loadingIcon) {
        loadingIcon.classList.remove("hidden");
      }
      newConfirmBtn.disabled = true;

      try {
        await onConfirm();
        this.closeConfirmationModal();
      } catch (error) {
        console.error("Erro na confirmação:", error);
      } finally {
        // Remover loading
        if (loadingIcon) {
          loadingIcon.classList.add("hidden");
        }
        newConfirmBtn.disabled = false;
      }
    });

    // Mostrar modal
    modal.classList.remove("hidden");
    document.body.style.overflow = "hidden";
  }

  /**
   * Fecha modal de confirmação
   */
  closeConfirmationModal() {
    const modal = document.getElementById("confirmationModal");
    if (modal) {
      modal.classList.add("hidden");
      document.body.style.overflow = "";
    }
  }

  /**
   * Exibe notificação toast
   */
  showToast(message, type = "info", duration = 5000) {
    const container = document.getElementById("toastContainer");
    if (!container) {
      // Fallback para console log apenas
      console.log(`[${type.toUpperCase()}] ${message}`);
      return;
    }

    const toastId = Date.now().toString();
    const typeClasses = {
      success: "bg-green-500 text-white",
      error: "bg-red-500 text-white",
      warning: "bg-yellow-500 text-white",
      info: "bg-blue-500 text-white",
    };

    const typeIcons = {
      success: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>`,
      error: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>`,
      warning: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16c-.77.833.192 2.5 1.732 2.5z"/>`,
      info: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>`,
    };

    const toast = document.createElement("div");
    toast.id = `toast-${toastId}`;
    toast.className = `${typeClasses[type] || typeClasses.info} rounded-lg shadow-lg p-4 transform transition-all duration-300 translate-x-full opacity-0`;

    toast.innerHTML = `
      <div class="flex items-center">
        <svg class="w-5 h-5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          ${typeIcons[type] || typeIcons.info}
        </svg>
        <p class="flex-1 text-sm font-medium">${this.escapeHtml(message)}</p>
        <button onclick="window.app.closeToast('${toastId}')" class="ml-3 text-white hover:text-gray-200">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>
    `;

    container.appendChild(toast);

    // Animar entrada
    setTimeout(() => {
      toast.classList.remove("translate-x-full", "opacity-0");
    }, 100);

    // Auto remover
    setTimeout(() => {
      this.closeToast(toastId);
    }, duration);
  }

  /**
   * Fecha toast específico
   */
  closeToast(toastId) {
    const toast = document.getElementById(`toast-${toastId}`);
    if (toast) {
      toast.classList.add("translate-x-full", "opacity-0");
      setTimeout(() => {
        if (toast.parentNode) {
          toast.parentNode.removeChild(toast);
        }
      }, 300);
    }
  }

  /**
   * Exporta atalhos para JSON
   */
  async exportShortcuts() {
    try {
      const includeStats =
        document.getElementById("includeStats")?.checked || false;
      const includeCategories =
        document.getElementById("includeCategories")?.checked || true;

      // Buscar atalhos
      const shortcutsResponse = await fetch(`${this.apiBaseUrl}shortcuts/`, {
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": this.csrfToken,
        },
      });

      if (!shortcutsResponse.ok) {
        throw new Error("Erro ao buscar atalhos");
      }

      const shortcutsData = await shortcutsResponse.json();
      const shortcuts = shortcutsData.results || shortcutsData;

      let exportData = {
        version: "1.0",
        exported_at: new Date().toISOString(),
        shortcuts: shortcuts.map((shortcut) => ({
          trigger: shortcut.trigger,
          title: shortcut.title,
          content: shortcut.content,
          expansion_type: shortcut.expansion_type,
          ai_prompt: shortcut.ai_prompt,
          variables: shortcut.variables,
          category_name: shortcut.category?.name || null,
          is_active: shortcut.is_active,
          use_count: includeStats ? shortcut.use_count : 0,
          created_at: shortcut.created_at,
        })),
      };

      if (includeCategories) {
        const categoriesResponse = await fetch(
          `${this.apiBaseUrl}categories/`,
          {
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": this.csrfToken,
            },
          },
        );

        if (categoriesResponse.ok) {
          const categoriesData = await categoriesResponse.json();
          exportData.categories = (
            categoriesData.results || categoriesData
          ).map((cat) => ({
            name: cat.name,
            description: cat.description,
            color: cat.color,
          }));
        }
      }

      // Criar e baixar arquivo
      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: "application/json",
      });

      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `symplifika-atalhos-${new Date().toISOString().split("T")[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      this.showToast("Atalhos exportados com sucesso!", "success");
    } catch (error) {
      console.error("Erro ao exportar atalhos:", error);
      this.showToast("Erro ao exportar atalhos", "error");
    }
  }

  /**
   * Importa atalhos de arquivo JSON
   */
  async importShortcuts() {
    const fileInput = document.getElementById("importFile");
    const overwriteExisting =
      document.getElementById("overwriteExisting")?.checked || false;

    if (!fileInput?.files || fileInput.files.length === 0) {
      this.showToast("Selecione um arquivo para importar", "warning");
      return;
    }

    const file = fileInput.files[0];

    if (file.type !== "application/json") {
      this.showToast("Arquivo deve ser do tipo JSON", "error");
      return;
    }

    try {
      const text = await file.text();
      const importData = JSON.parse(text);

      // Validar estrutura
      if (!importData.shortcuts || !Array.isArray(importData.shortcuts)) {
        throw new Error("Formato de arquivo inválido");
      }

      let importedCount = 0;
      let skippedCount = 0;
      let errorCount = 0;

      // Importar categorias primeiro (se existirem)
      if (importData.categories && Array.isArray(importData.categories)) {
        for (const categoryData of importData.categories) {
          try {
            // Verificar se categoria já existe
            const existingCategory = this.categories.find(
              (c) => c.name === categoryData.name,
            );

            if (!existingCategory) {
              await fetch(`${this.apiBaseUrl}categories/`, {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                  "X-CSRFToken": this.csrfToken,
                },
                body: JSON.stringify(categoryData),
              });
            }
          } catch (error) {
            console.warn(
              "Erro ao importar categoria:",
              categoryData.name,
              error,
            );
          }
        }

        // Recarregar categorias
        await this.loadCategories();
      }

      // Importar atalhos
      for (const shortcutData of importData.shortcuts) {
        try {
          // Verificar se atalho já existe
          const existingShortcut = this.shortcuts.find(
            (s) => s.trigger === shortcutData.trigger,
          );

          if (existingShortcut && !overwriteExisting) {
            skippedCount++;
            continue;
          }

          // Encontrar categoria por nome
          let categoryId = null;
          if (shortcutData.category_name) {
            const category = this.categories.find(
              (c) => c.name === shortcutData.category_name,
            );
            categoryId = category?.id || null;
          }

          const shortcutPayload = {
            trigger: shortcutData.trigger,
            title: shortcutData.title,
            content: shortcutData.content,
            expansion_type: shortcutData.expansion_type || "static",
            ai_prompt: shortcutData.ai_prompt || "",
            variables: shortcutData.variables || {},
            category: categoryId,
            is_active: shortcutData.is_active !== false,
          };

          const method = existingShortcut && overwriteExisting ? "PUT" : "POST";
          const url =
            existingShortcut && overwriteExisting
              ? `${this.apiBaseUrl}shortcuts/${existingShortcut.id}/`
              : `${this.apiBaseUrl}shortcuts/`;

          const response = await fetch(url, {
            method: method,
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": this.csrfToken,
            },
            body: JSON.stringify(shortcutPayload),
          });

          if (response.ok) {
            importedCount++;
          } else {
            errorCount++;
            console.error("Erro ao importar atalho:", shortcutData.trigger);
          }
        } catch (error) {
          errorCount++;
          console.error(
            "Erro ao processar atalho:",
            shortcutData.trigger,
            error,
          );
        }
      }

      // Mostrar resultado
      let message = `Importação concluída: ${importedCount} importados`;
      if (skippedCount > 0) message += `, ${skippedCount} ignorados`;
      if (errorCount > 0) message += `, ${errorCount} erros`;

      this.showToast(message, importedCount > 0 ? "success" : "warning");

      // Recarregar dados
      if (importedCount > 0) {
        await this.loadAllShortcuts();
        await this.loadRecentShortcuts();
        await this.loadDashboardStats();
      }

      // Limpar formulário
      fileInput.value = "";

      // Adicionar ao histórico
      this.addImportHistory({
        date: new Date().toISOString(),
        filename: file.name,
        imported: importedCount,
        skipped: skippedCount,
        errors: errorCount,
      });
    } catch (error) {
      console.error("Erro ao importar arquivo:", error);
      this.showToast("Erro ao processar arquivo de importação", "error");
    }
  }

  /**
   * Adiciona entrada ao histórico de importações
   */
  addImportHistory(entry) {
    const container = document.getElementById("importHistory");
    if (!container) return;

    // Remover estado vazio
    const emptyState = container.querySelector(".text-center");
    if (emptyState) {
      container.innerHTML = "";
    }

    const historyItem = document.createElement("div");
    historyItem.className =
      "flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg";

    historyItem.innerHTML = `
      <div>
        <p class="text-sm font-medium text-gray-900 dark:text-white">
          ${this.escapeHtml(entry.filename)}
        </p>
        <p class="text-xs text-gray-500 dark:text-gray-400">
          ${new Date(entry.date).toLocaleString()}
        </p>
      </div>
      <div class="text-right">
        <p class="text-sm text-green-600 dark:text-green-400">
          ${entry.imported} importados
        </p>
        ${entry.skipped > 0 ? `<p class="text-xs text-yellow-600 dark:text-yellow-400">${entry.skipped} ignorados</p>` : ""}
        ${entry.errors > 0 ? `<p class="text-xs text-red-600 dark:text-red-400">${entry.errors} erros</p>` : ""}
      </div>
    `;

    container.insertBefore(historyItem, container.firstChild);
  }

  /**
   * Exclui uma categoria
   */
  async deleteCategory(categoryId) {
    if (
      !confirm(
        "Tem certeza que deseja excluir esta categoria? Esta ação não pode ser desfeita.",
      )
    ) {
      return;
    }
    try {
      const response = await fetch(
        `${this.apiBaseUrl}categories/${categoryId}/`,
        {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": this.csrfToken,
          },
        },
      );
      if (!response.ok) {
        throw new Error("Erro ao excluir categoria");
      }
      this.showNotification("Categoria excluída com sucesso!", "success");
      await this.loadCategories();
    } catch (error) {
      console.error("Erro ao excluir categoria:", error);
      this.showNotification(
        error.message || "Erro ao excluir categoria",
        "error",
      );
    }
  }

  /**
   * Salva configurações do usuário
   */
  async saveSettings() {
    try {
      const form = document.getElementById("settingsForm");
      if (!form) return;

      const formData = new FormData(form);
      const settings = {};

      for (let [key, value] of formData.entries()) {
        settings[key] = value;
      }

      // Adicionar configurações de checkboxes
      const checkboxes = form.querySelectorAll('input[type="checkbox"]');
      checkboxes.forEach((checkbox) => {
        settings[checkbox.name || checkbox.id] = checkbox.checked;
      });

      // Salvar no localStorage e/ou enviar para API
      localStorage.setItem("symplifika_settings", JSON.stringify(settings));

      // Aplicar configurações imediatamente
      this.applySettings(settings);

      this.showToast("Configurações salvas com sucesso!", "success");
    } catch (error) {
      console.error("Erro ao salvar configurações:", error);
      this.showToast("Erro ao salvar configurações", "error");
    }
  }

  /**
   * Aplica configurações salvas
   */
  applySettings(settings) {
    // Aplicar tema
    if (settings.theme) {
      document.documentElement.className =
        settings.theme === "dark" ? "dark" : "";
    }

    // Outras configurações podem ser aplicadas aqui
    console.log("Configurações aplicadas:", settings);
  }

  /**
   * Exibe todas as categorias na página de categorias
   */
  displayAllCategories(categories) {
    const container = document.getElementById("categoriesList");
    if (!container) return;

    if (!categories || categories.length === 0) {
      container.innerHTML = `
        <div class="col-span-full flex flex-col items-center justify-center py-12 text-gray-500 dark:text-gray-400">
          <svg class="w-16 h-16 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M13 10V3L4 14h7v7l9-11h-7z"/>
          </svg>
          <h3 class="text-xl font-semibold mb-2">Nenhuma categoria encontrada</h3>
          <p class="mb-6">Crie sua primeira categoria para organizar seus atalhos!</p>
          <button class="btn btn-primary" onclick="window.app.openCreateCategoryModal()">Criar Categoria</button>
        </div>
      `;
      return;
    }

    container.innerHTML = categories
      .map(
        (category) => `
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-200 dark:border-gray-700 flex flex-col h-full">
          <div class="flex items-center mb-4">
            <span class="inline-block w-6 h-6 rounded-full mr-3" style="background-color: ${category.color || "#a3a3a3"}"></span>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white break-words">${this.escapeHtml(category.name || "")}</h3>
          </div>
          <p class="text-sm text-gray-600 dark:text-gray-300 flex-1 break-words mb-4">${this.escapeHtml(category.description || "Sem descrição")}</p>
          <div class="flex items-center justify-between mt-auto">
            <button class="btn btn-sm btn-outline" onclick="window.app.populateCategoryForm(${category.id})">Editar</button>
            <button
              class="ml-2 text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300 p-2 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
              title="Excluir categoria"
              onclick="window.app.deleteCategory && window.app.deleteCategory(${category.id})"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
              </svg>
            </button>
            <span class="text-xs text-gray-500 dark:text-gray-400">${category.shortcuts_count || 0} atalhos</span>
          </div>
        </div>
      `,
      )
      .join("");
  }

  /**
   * Carrega configurações salvas
   */
  loadSettings() {
    try {
      const savedSettings = localStorage.getItem("symplifika_settings");
      if (savedSettings) {
        const settings = JSON.parse(savedSettings);
        this.applySettings(settings);

        // Preencher formulário de configurações
        const form = document.getElementById("settingsForm");
        if (form) {
          Object.entries(settings).forEach(([key, value]) => {
            const input = form.querySelector(`[name="${key}"], #${key}`);
            if (input) {
              if (input.type === "checkbox") {
                input.checked = Boolean(value);
              } else if (input.type === "radio") {
                const radio = form.querySelector(
                  `[name="${key}"][value="${value}"]`,
                );
                if (radio) radio.checked = true;
              } else {
                input.value = value;
              }
            }
          });
        }
      }
    } catch (error) {
      console.error("Erro ao carregar configurações:", error);
    }
  }

  /**
   * Configura formulário de configurações
   */
  setupSettingsForm() {
    const settingsForm = document.getElementById("settingsForm");
    if (settingsForm) {
      settingsForm.addEventListener("submit", (e) => {
        e.preventDefault();
        this.saveSettings();
      });
    }

    // Eventos para alteração de tema
    const themeRadios = document.querySelectorAll('input[name="theme"]');
    themeRadios.forEach((radio) => {
      radio.addEventListener("change", (e) => {
        this.applyTheme(e.target.value);
      });
    });

    // Auto-salvar configurações em mudanças
    const autoSaveInputs = document.querySelectorAll(
      "#settingsForm input, #settingsForm select",
    );
    autoSaveInputs.forEach((input) => {
      input.addEventListener("change", () => {
        setTimeout(() => this.saveSettings(), 100);
      });
    });
  }

  /**
   * Aplica tema específico
   */
  applyTheme(theme) {
    if (theme === "dark") {
      document.documentElement.classList.add("dark");
    } else if (theme === "light") {
      document.documentElement.classList.remove("dark");
    } else {
      // Auto theme - detectar preferência do sistema
      if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
        document.documentElement.classList.add("dark");
      } else {
        document.documentElement.classList.remove("dark");
      }
    }
  }

  /**
   * Escapa HTML
   */
  escapeHtml(unsafe) {
    if (typeof unsafe !== "string") {
      unsafe = unsafe == null ? "" : String(unsafe);
    }
    return unsafe
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
}

// Inicializar aplicação quando DOM estiver carregado
document.addEventListener("DOMContentLoaded", () => {
  window.app = new SymphilikaApp();

  // Configurar eventos globais
  window.app.setupGlobalEvents();
});

// Compatibilidade com código legado
if (typeof window !== "undefined") {
  window.app = window.app || {};
}
