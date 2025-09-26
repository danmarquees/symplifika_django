// Background Script para Symplifika Chrome Extension (Vue.js)
// Gerencia autenticação, sincronização e comunicação com API

const API_BASE_URL = "http://127.0.0.1:8000";

// Estado da extensão
let extensionState = {
  isAuthenticated: false,
  user: null,
  token: null,
  refreshToken: null,
  shortcuts: [],
  lastSync: null,
};

// Restaurar estado do storage
async function restoreState() {
  try {
    const result = await chrome.storage.local.get([
      "token",
      "refreshToken",
      "user",
      "shortcuts",
      "lastSync",
    ]);

    if (result.token) {
      extensionState.token = result.token;
      extensionState.isAuthenticated = true;
    }

    if (result.refreshToken) {
      extensionState.refreshToken = result.refreshToken;
    }

    if (result.user) {
      extensionState.user = result.user;
    }

    if (result.shortcuts) {
      extensionState.shortcuts = result.shortcuts;
      console.log(
        `📦 ${result.shortcuts.length} atalhos restaurados do storage`,
      );
    }

    if (result.lastSync) {
      extensionState.lastSync = result.lastSync;
    }

    console.log("📦 Estado restaurado:", {
      authenticated: extensionState.isAuthenticated,
      user: extensionState.user?.username,
      shortcuts: extensionState.shortcuts?.length || 0,
    });
  } catch (error) {
    console.error("❌ Erro ao restaurar estado:", error);
  }
}

// Salvar estado no storage
async function saveState() {
  try {
    await chrome.storage.local.set({
      token: extensionState.token,
      refreshToken: extensionState.refreshToken,
      user: extensionState.user,
      shortcuts: extensionState.shortcuts,
      lastSync: extensionState.lastSync,
    });
  } catch (error) {
    console.error("❌ Erro ao salvar estado:", error);
  }
}

// Função para refresh do token JWT
async function refreshAccessToken() {
  if (!extensionState.refreshToken) {
    console.warn("⚠️ Não há refresh token disponível");
    return { success: false, error: "Sem refresh token" };
  }

  try {
    console.log("🔄 Tentando refresh do token...");

    const response = await fetch(`${API_BASE_URL}/api/token/refresh/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Origin: chrome.runtime.getURL(""),
      },
      body: JSON.stringify({
        refresh: extensionState.refreshToken,
      }),
    });

    console.log("📡 Status da resposta refresh:", response.status);

    if (response.ok) {
      const data = await response.json();
      console.log("✅ Token refreshed com sucesso");

      // Atualizar token de acesso
      extensionState.token = data.access;
      
      // Se vier um novo refresh token, atualizar também
      if (data.refresh) {
        extensionState.refreshToken = data.refresh;
      }

      // Salvar no storage
      await saveState();

      return {
        success: true,
        token: extensionState.token,
        refreshToken: extensionState.refreshToken,
      };
    } else {
      console.error("❌ Erro no refresh do token:", response.status);
      
      // Se o refresh token também expirou, fazer logout
      if (response.status === 401) {
        console.log("🚪 Refresh token expirado, fazendo logout...");
        await handleLogout();
        return { success: false, error: "Refresh token expirado", requiresLogin: true };
      }
      
      return { success: false, error: `Erro HTTP ${response.status}` };
    }
  } catch (error) {
    console.error("❌ Erro de conexão no refresh:", error);
    return { success: false, error: `Erro de conexão: ${error.message}` };
  }
}

// Função para fazer requisições autenticadas com retry automático
async function authenticatedFetch(url, options = {}) {
  if (!extensionState.token) {
    return { success: false, error: "Não autenticado", requiresLogin: true };
  }

  // Primeira tentativa com token atual
  const requestOptions = {
    ...options,
    headers: {
      ...options.headers,
      Authorization: `Bearer ${extensionState.token}`,
      "Content-Type": "application/json",
    },
  };

  try {
    let response = await fetch(url, requestOptions);

    // Se token expirou, tentar refresh
    if (response.status === 401) {
      console.log("🔄 Token expirado, tentando refresh...");
      
      const refreshResult = await refreshAccessToken();
      
      if (refreshResult.success) {
        // Retry com novo token
        requestOptions.headers.Authorization = `Bearer ${extensionState.token}`;
        response = await fetch(url, requestOptions);
      } else {
        return {
          success: false,
          error: "Token expirado e refresh falhou",
          requiresLogin: refreshResult.requiresLogin || false,
        };
      }
    }

    return {
      success: response.ok,
      response: response,
      status: response.status,
    };
  } catch (error) {
    console.error("❌ Erro na requisição autenticada:", error);
    return { success: false, error: `Erro de conexão: ${error.message}` };
  }
}

// Tentativa de login automático via sessão Django
async function tryAutoLogin() {
  try {
    console.log("🔄 Tentando login automático via sessão Django...");

    const response = await fetch(
      `${API_BASE_URL}/users/api/auth/check-session/`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Origin: chrome.runtime.getURL(""),
        },
        credentials: "include", // Incluir cookies de sessão
      },
    );

    console.log("📡 Status da resposta auto-login:", response.status);

    if (response.ok) {
      const data = await response.json();
      console.log("📄 Dados da resposta auto-login:", data);

      if (data.authenticated && data.access) {
        // Login automático bem-sucedido
        extensionState.token = data.access;
        extensionState.user = data.user;
        extensionState.isAuthenticated = true;

        // Salvar no storage
        await saveState();

        // Sincronizar atalhos
        await syncShortcuts();

        console.log(
          "✅ Login automático realizado com sucesso:",
          extensionState.user.username,
        );

        return {
          success: true,
          user: extensionState.user,
          token: extensionState.token,
          message: "Login automático via sessão Django",
        };
      }
    }

    console.log("ℹ️ Usuário não está logado na aplicação principal");
    return {
      success: false,
      error: "Usuário não está logado na aplicação principal",
    };
  } catch (error) {
    console.error("❌ Erro no login automático:", error);
    return { success: false, error: "Erro de conexão no login automático" };
  }
}

// Listener para mensagens do popup e content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  // Verificar se a extensão ainda está ativa
  if (!chrome.runtime?.id) {
    console.warn(
      "⚠️ Extensão foi invalidada durante processamento de mensagem",
    );
    sendResponse({ success: false, error: "Extensão invalidada" });
    return false;
  }

  console.log("📨 Mensagem recebida:", request.type);

  // Processar de forma assíncrona
  (async () => {
    try {
      let response;

      switch (request.type) {
        case "LOGIN":
          response = await handleLogin(request.payload);
          break;

        case "AUTO_LOGIN":
          response = await tryAutoLogin();
          break;

        case "LOGOUT":
          response = await handleLogout();
          break;

        case "SYNC_SHORTCUTS":
          response = await syncShortcuts();
          break;

        case "GET_SHORTCUTS":
          console.log(
            `📋 GET_SHORTCUTS solicitado. Estado atual:`,
            {
              authenticated: extensionState.isAuthenticated,
              shortcuts: extensionState.shortcuts.length,
              user: extensionState.user?.username,
              lastSync: extensionState.lastSync ? new Date(extensionState.lastSync).toLocaleString() : 'nunca'
            }
          );
          
          // Se não há atalhos e está autenticado, tentar sincronizar
          if (extensionState.shortcuts.length === 0 && extensionState.isAuthenticated) {
            console.log("🔄 Nenhum atalho em cache, tentando sincronizar...");
            try {
              const syncResult = await syncShortcuts();
              if (syncResult.success) {
                console.log(`✅ Sincronização bem-sucedida: ${extensionState.shortcuts.length} atalhos`);
              } else {
                console.warn("⚠️ Falha na sincronização:", syncResult.error);
              }
            } catch (syncError) {
              console.error("❌ Erro na sincronização automática:", syncError);
            }
          }
          
          response = {
            success: true,
            shortcuts: extensionState.shortcuts,
            lastSync: extensionState.lastSync,
            authenticated: extensionState.isAuthenticated,
            user: extensionState.user?.username
          };
          break;

        case "EXPAND_TEXT":
          response = await handleTextExpansion(request.payload);
          break;

        case "USE_SHORTCUT":
          response = await markShortcutAsUsed(request.payload.shortcutId);
          break;

        case "REFRESH_TOKEN":
          response = await refreshAccessToken();
          break;

        case "PING":
          response = {
            success: true,
            status: "alive",
            authenticated: extensionState.isAuthenticated,
            shortcuts: extensionState.shortcuts.length,
            timestamp: Date.now(),
          };
          break;

        default:
          response = {
            success: false,
            error: "Comando desconhecido: " + request.type,
          };
      }

      // Verificar se ainda podemos enviar resposta
      if (chrome.runtime?.id && sendResponse) {
        try {
          sendResponse(response);
        } catch (sendError) {
          console.warn("⚠️ Erro ao enviar resposta:", sendError.message);
        }
      }
    } catch (error) {
      console.error("❌ Erro no background script:", error);
      if (chrome.runtime?.id && sendResponse) {
        try {
          sendResponse({ success: false, error: error.message });
        } catch (sendError) {
          console.warn(
            "⚠️ Erro ao enviar resposta de erro:",
            sendError.message,
          );
        }
      }
    }
  })();

  // Retornar true para manter o canal de comunicação aberto
  return true;
});

// Função de login
async function handleLogin(credentials) {
  try {
    console.log("🔐 Tentando login para:", credentials.login);
    console.log("🌐 URL da API:", `${API_BASE_URL}/api/token/`);

    const response = await fetch(`${API_BASE_URL}/api/token/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Origin: chrome.runtime.getURL(""),
      },
      body: JSON.stringify({
        login: credentials.login,
        password: credentials.password,
      }),
    });

    console.log("📡 Status da resposta:", response.status, response.statusText);

    let data;
    try {
      data = await response.json();
      console.log("📄 Dados da resposta:", data);
    } catch (jsonError) {
      console.error("❌ Erro ao parsear JSON:", jsonError);
      const textData = await response.text();
      console.log("📄 Resposta como texto:", textData);
      return {
        success: false,
        error: `Erro no servidor (${response.status}): ${textData.substring(0, 100)}`,
      };
    }

    if (response.ok && data.access) {
      // Login bem-sucedido
      extensionState.token = data.access;
      extensionState.refreshToken = data.refresh; // Armazenar refresh token
      extensionState.user = data.user;
      extensionState.isAuthenticated = true;

      // Salvar no storage
      await saveState();

      // Sincronizar atalhos
      await syncShortcuts();

      console.log(
        "✅ Login realizado com sucesso:",
        extensionState.user.username,
      );

      return {
        success: true,
        user: extensionState.user,
        token: extensionState.token,
      };
    } else {
      console.error("❌ Erro no login:", data);
      return {
        success: false,
        error:
          data.error ||
          data.detail ||
          data.message ||
          `Erro HTTP ${response.status}`,
      };
    }
  } catch (error) {
    console.error("❌ Erro de conexão no login:", error);
    return {
      success: false,
      error: `Erro de conexão: ${error.message}. Verifique se o servidor Django está rodando em ${API_BASE_URL}`,
    };
  }
}

// Função de logout
async function handleLogout() {
  try {
    // Limpar estado
    extensionState = {
      isAuthenticated: false,
      user: null,
      token: null,
      refreshToken: null,
      shortcuts: [],
      lastSync: null,
    };

    // Limpar storage
    await chrome.storage.local.clear();

    console.log("👋 Logout realizado");

    return { success: true };
  } catch (error) {
    console.error("❌ Erro no logout:", error);
    return { success: false, error: "Erro no logout" };
  }
}

// Sincronizar atalhos com a API
async function syncShortcuts() {
  if (!extensionState.isAuthenticated || !extensionState.token) {
    return { success: false, error: "Não autenticado" };
  }

  try {
    console.log("🔄 Sincronizando atalhos...");

    const result = await authenticatedFetch(`${API_BASE_URL}/shortcuts/api/shortcuts/`, {
      method: "GET",
    });

    if (result.success && result.response.ok) {
      const data = await result.response.json();
      extensionState.shortcuts = data.results || data || [];
      extensionState.lastSync = Date.now();

      // Salvar no storage
      await saveState();

      console.log(
        `✅ ${extensionState.shortcuts.length} atalhos sincronizados`,
      );

      return {
        success: true,
        shortcuts: extensionState.shortcuts,
        lastSync: extensionState.lastSync,
      };
    } else {
      console.error("❌ Erro na sincronização:", result.status || "desconhecido");
      
      if (result.requiresLogin) {
        return { success: false, error: "Requer novo login", requiresLogin: true };
      }
      
      return { success: false, error: result.error || "Erro na API" };
    }
  } catch (error) {
    console.error("❌ Erro de conexão na sincronização:", error);
    return { success: false, error: "Erro de conexão" };
  }
}

// Marcar atalho como usado
async function markShortcutAsUsed(shortcutId) {
  if (!extensionState.isAuthenticated || !extensionState.token) {
    return { success: false, error: "Não autenticado" };
  }

  try {
    const result = await authenticatedFetch(
      `${API_BASE_URL}/shortcuts/api/shortcuts/${shortcutId}/use/`,
      {
        method: "POST",
      },
    );

    if (result.success && result.response.ok) {
      console.log(`✅ Atalho ${shortcutId} marcado como usado`);
      return { success: true };
    } else {
      console.error("❌ Erro ao marcar atalho como usado:", result.status || "desconhecido");
      
      if (result.requiresLogin) {
        return { success: false, error: "Requer novo login", requiresLogin: true };
      }
      
      return { success: false, error: result.error || "Erro na API" };
    }
  } catch (error) {
    console.error("❌ Erro de conexão ao marcar uso:", error);
    return { success: false, error: "Erro de conexão" };
  }
}

// Expandir texto com atalho
async function handleTextExpansion(payload) {
  const { trigger } = payload;

  // Procurar atalho pelo trigger
  const shortcut = extensionState.shortcuts.find(
    (s) => s.trigger === trigger && s.is_active,
  );

  if (!shortcut) {
    return { success: false, error: "Atalho não encontrado" };
  }

  try {
    // Processar template com variáveis
    let expandedText = shortcut.content;

    // Variáveis básicas
    const now = new Date();
    const variables = {
      "user.name":
        extensionState.user?.first_name || extensionState.user?.username || "",
      "user.email": extensionState.user?.email || "",
      "date.today": now.toLocaleDateString("pt-BR"),
      "date.time": now.toLocaleTimeString("pt-BR"),
      "date.year": now.getFullYear().toString(),
      "date.month": (now.getMonth() + 1).toString().padStart(2, "0"),
      "date.day": now.getDate().toString().padStart(2, "0"),
    };

    // Substituir variáveis
    for (const [key, value] of Object.entries(variables)) {
      const regex = new RegExp(`{{\\s*${key}\\s*}}`, "g");
      expandedText = expandedText.replace(regex, value);
    }

    // Marcar como usado (opcional - não bloquear se falhar)
    try {
      await authenticatedFetch(
        `${API_BASE_URL}/shortcuts/api/shortcuts/${shortcut.id}/use/`,
        {
          method: "POST",
        },
      );
    } catch (error) {
      console.warn("⚠️ Não foi possível marcar atalho como usado:", error);
    }

    console.log(
      "✨ Texto expandido:",
      trigger,
      "->",
      expandedText.substring(0, 50) + "...",
    );

    return {
      success: true,
      expandedText: expandedText,
      shortcut: shortcut,
    };
  } catch (error) {
    console.error("❌ Erro na expansão:", error);
    return { success: false, error: "Erro na expansão" };
  }
}

// Alarme de sincronização automática
if (chrome.alarms) {
  chrome.alarms.onAlarm.addListener(async (alarm) => {
    if (alarm.name === "syncShortcuts" && extensionState.isAuthenticated) {
      console.log("⏰ Sincronização automática iniciada");
      await syncShortcuts();
    }
  });
}

// Listeners para service worker (Manifest V3)
if (chrome.runtime.onStartup) {
  chrome.runtime.onStartup.addListener(async () => {
    console.log("🚀 Service worker iniciado");
    await restoreState();

    if (extensionState.isAuthenticated) {
      console.log("🔄 Sincronização na inicialização");
      await syncShortcuts();
    }
  });
}

// Listener para quando a extensão é instalada/atualizada
if (chrome.runtime.onInstalled) {
  chrome.runtime.onInstalled.addListener(async (details) => {
    console.log("📦 Extensão instalada/atualizada:", details.reason);
    await restoreState();

    if (extensionState.isAuthenticated) {
      console.log("🔄 Sincronização após instalação");
      await syncShortcuts();
    }
  });
}

// Inicialização imediata do background script
(async () => {
  await restoreState();

  if (extensionState.isAuthenticated) {
    console.log("🔄 Sincronização na inicialização do background");
    await syncShortcuts();
  } else {
    // Tentar login automático se não estiver autenticado
    console.log("🔄 Tentando login automático na inicialização...");
    const autoLoginResult = await tryAutoLogin();
    if (autoLoginResult.success) {
      console.log("✅ Login automático bem-sucedido na inicialização");
    } else {
      console.log("ℹ️ Login automático não disponível:", autoLoginResult.error);
    }
  }
})();

console.log("🎯 Background script carregado - Symplifika v2.0.0");
