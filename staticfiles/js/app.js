/**
 * Symplifika Dashboard Application
 * Gerencia a interface do dashboard e integração com APIs
 */

class SymphilikaApp {
  constructor() {
    this.apiBaseUrl = "/shortcuts/api";
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

    // Eventos de interface
    document.addEventListener("DOMContentLoaded", () => {
      this.loadRecentShortcuts();
      this.loadDashboardStats();
    });
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
      const response = await fetch(`${this.apiBaseUrl}/categories/`, {
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
        `${this.apiBaseUrl}/shortcuts/?ordering=-last_used&page_size=5`,
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
      const response = await fetch(`${this.apiBaseUrl}/shortcuts/stats/`, {
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
        ? `${this.apiBaseUrl}/shortcuts/${shortcutId}/`
        : `${this.apiBaseUrl}/shortcuts/`;

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

      const categoryId = data.category_id;
      const isEdit = categoryId && categoryId !== "";

      const url = isEdit
        ? `${this.apiBaseUrl}/categories/${categoryId}/`
        : `${this.apiBaseUrl}/categories/`;

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
        throw new Error(errorData.detail || "Erro ao salvar categoria");
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
      this.showNotification(
        error.message || "Erro ao salvar categoria",
        "error",
      );
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
                    <button
                        onclick="window.app.useShortcut(${shortcut.id})"
                        class="text-symplifika-primary hover:text-symplifika-primary-dark"
                        title="Usar atalho"
                    >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                        </svg>
                    </button>
                </div>
            </div>
        `,
      )
      .join("");
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
    // Implementar conforme necessário baseado na estrutura do dashboard
    console.log("Stats loaded:", stats);
  }

  /**
   * Usa um atalho
   */
  async useShortcut(shortcutId, context = "") {
    try {
      const response = await fetch(
        `${this.apiBaseUrl}/shortcuts/${shortcutId}/use/`,
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

    // Usar toast/notification existente se disponível
    if (window.Symplifika && window.Symplifika.Toast) {
      window.Symplifika.Toast.show(message, type);
    } else {
      // Fallback para alert
      alert(message);
    }
  }

  /**
   * Escapa HTML
   */
  escapeHtml(unsafe) {
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
});

// Compatibilidade com código legado
if (typeof window !== "undefined") {
  window.app = window.app || {};
}
