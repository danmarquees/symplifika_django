<template>
  <div class="popup-container">
    <!-- Header -->
    <div class="header">
      <div class="logo-container">
        <div class="logo-icon">S</div>
        <div class="logo-text">
          <div class="logo-title">Symplifika</div>
          <div class="subtitle">Atalhos de Texto Inteligentes</div>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div class="content">
      <!-- Loading State -->
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <div class="loading-text">Carregando...</div>
      </div>

      <!-- Auto-login Message -->
      <div v-else-if="tryingAutoLogin" class="auto-login-message">
        <div class="auto-login-icon">🔄</div>
        <div class="auto-login-text">
          <div class="auto-login-title">Login Automático</div>
          <div class="auto-login-subtitle">Verificando se você está logado na aplicação principal...</div>
        </div>
      </div>

      <!-- Login Form -->
      <div v-else-if="!isAuthenticated" class="login-form">
        <h3>Entre na sua conta</h3>

        <!-- Auto-login Info -->
        <div v-if="showAutoLoginTip" class="info-message">
          💡 <strong>Dica:</strong> Faça login na aplicação principal para entrar automaticamente na extensão!
        </div>

        <!-- Error Message -->
        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <!-- Success Message -->
        <div v-if="success" class="success-message">
          {{ success }}
        </div>

        <form @submit.prevent="login">
          <div class="form-group">
            <label class="form-label">Email ou Nome de Usuário</label>
            <input
              v-model="loginData.login"
              type="text"
              class="form-input"
              placeholder="seu@email.com ou username"
              :disabled="loggingIn"
              required
            />
          </div>

          <div class="form-group">
            <label class="form-label">Senha</label>
            <input
              v-model="loginData.password"
              type="password"
              class="form-input"
              placeholder="••••••••"
              :disabled="loggingIn"
              required
            />
          </div>

          <button
            type="submit"
            class="btn btn-primary"
            :disabled="loggingIn || !loginData.login || !loginData.password"
          >
            <span v-if="loggingIn">Entrando...</span>
            <span v-else>Entrar</span>
          </button>
        </form>

        <div class="action-buttons" style="justify-content: center; margin-top: 20px;">
          <button
            @click="openDashboard"
            class="btn-secondary"
          >
            Não tem conta? Criar uma nova
          </button>
        </div>
      </div>

      <!-- Shortcuts List -->
      <div v-else class="shortcuts-list">
        <h3>
          Seus Atalhos
          <button @click="logout" class="logout-btn">
            Sair
          </button>
        </h3>

        <!-- User Info -->
        <div v-if="user" class="user-info">
          <div class="user-name">{{ user.first_name || user.username }}</div>
          <div class="user-email">{{ user.email }}</div>
          <div class="user-stats">
            <span>{{ shortcuts.length }} atalhos</span>
            <span class="plan-badge" :class="user.is_premium ? 'plan-premium' : 'plan-free'">
              {{ user.is_premium ? 'Premium' : 'Gratuito' }}
            </span>
          </div>
        </div>

        <!-- Shortcuts -->
        <div v-if="shortcuts.length > 0">
          <div v-for="shortcut in shortcuts.slice(0, 8)" :key="shortcut.id" class="shortcut-item">
            <div class="shortcut-info">
              <div class="shortcut-title">{{ shortcut.title }}</div>
              <div class="shortcut-preview">
                {{ shortcut.content.substring(0, 45) }}{{ shortcut.content.length > 45 ? '...' : '' }}
              </div>
            </div>
            <div class="shortcut-trigger">{{ shortcut.trigger }}</div>
          </div>

          <div v-if="shortcuts.length > 8" class="action-buttons" style="justify-content: center; margin-top: 20px;">
            <button @click="openDashboard" class="btn-success">
              Ver todos ({{ shortcuts.length }})
            </button>
          </div>
        </div>

        <div v-else class="empty-state">
          <div class="empty-state-icon">📝</div>
          <div class="empty-state-text">Nenhum atalho encontrado</div>
          <button @click="openDashboard" class="btn-success">
            Criar primeiro atalho
          </button>
        </div>

        <!-- Mode Toggle -->
        <div class="action-buttons" style="justify-content: center; margin-top: 20px; padding-top: 20px; border-top: 1px solid var(--symplifika-gray-100);">
          <button @click="toggleMode" :disabled="togglingMode" class="btn-secondary" style="margin-right: 10px;">
            <span v-if="togglingMode">Alterando...</span>
            <span v-else-if="quickActionMode">🎯 Modo: Ícone</span>
            <span v-else">⚡ Modo: Trigger</span>
          </button>
          <button @click="syncShortcuts" :disabled="syncing" class="btn-success">
            <span v-if="syncing">Sincronizando...</span>
            <span v-else">🔄 Sincronizar</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="footer">
      <div class="footer-text">
        Versão 2.0.0 • Vue.js • Made with ❤️
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      loading: true,
      isAuthenticated: false,
      loggingIn: false,
      syncing: false,
      togglingMode: false,
      quickActionMode: true,
      tryingAutoLogin: false,
      showAutoLoginTip: false,
      error: null,
      success: null,
      user: null,
      shortcuts: [],
      loginData: {
        login: '',
        password: ''
      }
    }
  },

  async mounted() {
    await this.checkAuth()
    this.loading = false
  },

  methods: {
    async checkAuth() {
      try {
        // Primeiro tentar auto-login via sessão Django
        await this.tryAutoLogin()

        // Verificar se há token armazenado
        const result = await chrome.storage.local.get(['token', 'user'])

        if (result.token && result.user) {
          this.isAuthenticated = true
          this.user = result.user

          // Garantir que o background script restaurou o estado
          await this.ensureBackgroundState()

          // Carregar atalhos
          await this.loadShortcuts()
        } else if (!this.isAuthenticated) {
          // Mostrar dica de auto-login se não conseguiu fazer login automaticamente
          this.showAutoLoginTip = true
        }
      } catch (error) {
        console.error('Erro na verificação de auth:', error)
      }
    },

    async tryAutoLogin() {
      try {
        this.tryingAutoLogin = true
        console.log('🔄 Tentando login automático...')

        const response = await chrome.runtime.sendMessage({ type: 'AUTO_LOGIN' })

        if (response && response.success) {
          console.log('✅ Login automático bem-sucedido:', response.user.username)

          this.isAuthenticated = true
          this.user = response.user
          this.success = `Bem-vindo, ${response.user.full_name || response.user.username}! Login automático realizado.`

          // Carregar atalhos
          await this.loadShortcuts()

          // Limpar mensagem de sucesso após 3s
          setTimeout(() => {
            this.success = null
          }, 3000)
        } else {
          console.log('ℹ️ Login automático não disponível:', response?.error)
        }
      } catch (error) {
        console.error('❌ Erro no auto-login:', error)
      } finally {
        this.tryingAutoLogin = false
      }
    },

    async ensureBackgroundState() {
      try {
        // Fazer ping no background para garantir que está ativo e com estado restaurado
        const pingResponse = await chrome.runtime.sendMessage({ type: 'PING' })

        if (pingResponse && pingResponse.success) {
          console.log('✅ Background script ativo:', pingResponse)

          // Se não está autenticado no background, mas temos token local, restaurar
          if (!pingResponse.authenticated) {
            console.log('🔄 Restaurando estado no background...')
            // O background vai restaurar automaticamente quando receber qualquer mensagem
          }
        }
      } catch (error) {
        console.warn('⚠️ Erro ao verificar background state:', error)
      }
    },

    async login() {
      if (!this.loginData.login || !this.loginData.password) {
        this.error = 'Preencha todos os campos'
        return
      }

      this.loggingIn = true
      this.error = null

      try {
        // Enviar mensagem para background script
        const response = await chrome.runtime.sendMessage({
          type: 'LOGIN',
          payload: {
            login: this.loginData.login,
            password: this.loginData.password
          }
        })

        if (response.success) {
          this.isAuthenticated = true
          this.user = response.user
          this.success = 'Login realizado com sucesso!'

          // Limpar formulário
          this.loginData = { login: '', password: '' }

          // Carregar atalhos
          await this.loadShortcuts()

          // Limpar mensagem de sucesso após 2s
          setTimeout(() => {
            this.success = null
          }, 2000)
        } else {
          this.error = response.error || 'Erro no login'
        }
      } catch (error) {
        console.error('Erro no login:', error)
        this.error = 'Erro de conexão. Verifique se o servidor está rodando.'
      } finally {
        this.loggingIn = false
      }
    },

    async logout() {
      try {
        await chrome.runtime.sendMessage({ type: 'LOGOUT' })
        this.isAuthenticated = false
        this.user = null
        this.shortcuts = []
      } catch (error) {
        console.error('Erro no logout:', error)
      }
    },

    async loadShortcuts() {
      try {
        const response = await chrome.runtime.sendMessage({ type: 'GET_SHORTCUTS' })

        if (response.success) {
          this.shortcuts = response.shortcuts || []
          console.log(`📋 ${this.shortcuts.length} atalhos carregados`)

          // Se não há atalhos no background, tentar sincronizar
          if (this.shortcuts.length === 0) {
            console.log('🔄 Nenhum atalho encontrado, tentando sincronizar...')
            await this.syncShortcuts()
          }
        } else {
          console.error('❌ Erro ao carregar atalhos:', response.error)
        }
      } catch (error) {
        console.error('❌ Erro ao carregar atalhos:', error)
      }
    },

    async syncShortcuts() {
      this.syncing = true
      this.error = null

      try {
        const response = await chrome.runtime.sendMessage({ type: 'SYNC_SHORTCUTS' })

        if (response && response.success) {
          this.shortcuts = response.shortcuts || []
          this.success = 'Atalhos sincronizados!'

          setTimeout(() => {
            this.success = null
          }, 2000)
        } else {
          console.error('❌ Erro na sincronização:', response)
          this.error = response?.error || 'Erro na sincronização'
        }
      } catch (error) {
        console.error('❌ Erro na sincronização:', error)
        this.error = 'Erro de conexão com a extensão'
      } finally {
        this.syncing = false
      }
    },

    async toggleMode() {
      this.togglingMode = true;
      this.error = null;

      try {
        // Alternar modo
        this.quickActionMode = !this.quickActionMode;

        // Enviar mensagem para content script
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        if (tab) {
          await chrome.tabs.sendMessage(tab.id, {
            type: 'TOGGLE_MODE',
            payload: { quickActionMode: this.quickActionMode }
          });
        }

        this.success = `Modo alterado para: ${this.quickActionMode ? 'Ícone de Ação' : 'Triggers Tradicionais'}`;

        setTimeout(() => {
          this.success = null;
        }, 2000);

      } catch (error) {
        console.error('Erro ao alternar modo:', error);
        this.error = 'Erro ao alternar modo';
        // Reverter mudança
        this.quickActionMode = !this.quickActionMode;
      } finally {
        this.togglingMode = false;
      }
    },

    openDashboard() {
      chrome.tabs.create({ url: 'http://127.0.0.1:8000/dashboard/' })
    }
  }
}
</script>

<style scoped>
/* Container principal - Alinhado com design moderno */
.popup-container {
  width: 400px;
  min-height: 600px;
  background: linear-gradient(135deg, #00ff57 0%, #00c853 100%);
  color: var(--symplifika-dark);
  font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  border-radius: 0;
  box-shadow: none;
  overflow: hidden;
  position: relative;
}

.popup-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
  pointer-events: none;
  z-index: 0;
}

/* Auto-login message - Modernizado */
.auto-login-message {
  display: flex;
  align-items: center;
  padding: 24px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  color: #1f2937;
  border-radius: 20px;
  margin: 28px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.3);
  animation: slideUp 0.4s ease-out;
  position: relative;
  z-index: 1;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.auto-login-icon {
  font-size: 24px;
  margin-right: 15px;
  animation: spin 2s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.auto-login-text {
  flex: 1;
}

.auto-login-title {
  font-weight: 700;
  font-size: 18px;
  margin-bottom: 6px;
  letter-spacing: -0.025em;
  color: #111827;
}

.auto-login-subtitle {
  font-size: 14px;
  opacity: 0.8;
  line-height: 1.5;
  color: #4b5563;
  font-weight: 500;
}

/* Info message - Modernizada */
.info-message {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border: 1px solid #0ea5e9;
  color: #0c4a6e;
  padding: 16px;
  border-radius: 12px;
  margin-bottom: 24px;
  font-size: 14px;
  line-height: 1.5;
  font-weight: 500;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

/* Header - Alinhado com design principal */
.header {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  padding: 24px;
  text-align: center;
  color: white;
  border-bottom: 1px solid rgba(255, 255, 255, 0.15);
  position: relative;
  z-index: 1;
}

.logo-container {
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-icon {
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 22px;
  margin-right: 12px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.logo-icon:hover {
  transform: scale(1.05);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.logo-title {
  font-size: 22px;
  font-weight: 700;
  margin-bottom: 4px;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  letter-spacing: -0.025em;
}

.subtitle {
  font-size: 12px;
  opacity: 0.9;
  font-weight: 500;
  letter-spacing: 0.025em;
}

.content {
  padding: 28px;
  position: relative;
  z-index: 1;
}

.loading {
  text-align: center;
  padding: 40px 20px;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 15px;
}

.loading-text {
  color: #666;
  font-size: 14px;
}

.login-form h3 {
  margin: 0 0 28px 0;
  text-align: center;
  color: #111827;
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.025em;
}

.form-group {
  margin-bottom: 15px;
}

.form-label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  font-size: 13px;
  color: var(--symplifika-dark);
}

.form-input {
  width: 100%;
  padding: 16px 18px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 500;
  box-sizing: border-box;
  transition: all 0.3s ease;
  background: #f9fafb;
  font-family: inherit;
}

.form-input:focus {
  outline: none;
  border-color: #00c853;
  background: white;
  box-shadow: 0 0 0 4px rgba(0, 200, 83, 0.1), 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  transform: translateY(-2px);
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  font-size: 14px;
  transition: all 0.3s;
  text-decoration: none;
  display: inline-block;
  text-align: center;
}

.btn-primary {
  background: linear-gradient(135deg, #00ff57 0%, #00c853 100%);
  color: white;
  width: 100%;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  box-shadow: 0 4px 12px rgba(0, 200, 83, 0.3);
  position: relative;
  overflow: hidden;
}

.btn-primary::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.btn-primary:hover::before {
  left: 100%;
}

.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0, 200, 83, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

.btn-success {
  background: #28a745;
  color: white;
}

.btn-success:hover {
  background: #218838;
}

.error-message {
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  border: 1px solid #fecaca;
  color: #dc2626;
  padding: 16px;
  border-radius: 12px;
  margin-bottom: 20px;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.error-message::before {
  content: '⚠️';
  font-size: 16px;
}

.success-message {
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
  border: 1px solid #bbf7d0;
  color: #4caf50;
  padding: 16px;
  border-radius: 12px;
  margin-bottom: 20px;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.success-message::before {
  content: '✅';
  font-size: 16px;
}

.action-buttons {
  display: flex;
  gap: 10px;
  justify-content: space-between;
  margin-top: 15px;
}

.footer {
  text-align: center;
  padding: 16px 24px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  z-index: 1;
}

.footer-text {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 400;
  letter-spacing: 0.025em;
}

:root {
  --symplifika-white: #ffffff;
  --symplifika-dark: #1a1a1a;
  --symplifika-gray-100: #f3f4f6;
  --symplifika-primary: #00c853;
  --symplifika-secondary: #00ff57;
}
</style>
