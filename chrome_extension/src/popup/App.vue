<template>
  <div class="popup-container">
    <!-- Header -->
    <div class="header">
      <div class="logo">Symplifika</div>
      <div class="subtitle">Atalhos de Texto Inteligentes</div>
    </div>

    <!-- Content -->
    <div class="content">
      <!-- Loading State -->
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <div>Carregando...</div>
      </div>

      <!-- Login Form -->
      <div v-else-if="!isAuthenticated" class="login-form">
        <h3 style="margin-top: 0; color: #374151; text-align: center;">Entre na sua conta</h3>
        
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

        <div style="text-align: center; margin-top: 16px;">
          <button 
            @click="openDashboard"
            style="background: none; border: none; color: #667eea; font-size: 12px; cursor: pointer;"
          >
            Não tem conta? Criar uma nova
          </button>
        </div>
      </div>

      <!-- Shortcuts List -->
      <div v-else class="shortcuts-list">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
          <h3 style="margin: 0; color: #374151;">Seus Atalhos</h3>
          <button @click="logout" style="background: #ef4444; color: white; border: none; padding: 6px 12px; border-radius: 6px; font-size: 12px; cursor: pointer;">
            Sair
          </button>
        </div>

        <!-- User Info -->
        <div v-if="user" style="background: #f9fafb; padding: 12px; border-radius: 8px; margin-bottom: 16px;">
          <div style="font-weight: 500; color: #374151;">{{ user.first_name || user.username }}</div>
          <div style="font-size: 12px; color: #6b7280;">{{ user.email }}</div>
          <div style="font-size: 11px; color: #9ca3af; margin-top: 4px;">
            {{ shortcuts.length }} atalhos • Plano: {{ user.is_premium ? 'Premium' : 'Gratuito' }}
          </div>
        </div>

        <!-- Shortcuts -->
        <div v-if="shortcuts.length > 0">
          <div v-for="shortcut in shortcuts.slice(0, 8)" :key="shortcut.id" class="shortcut-item">
            <div>
              <div class="shortcut-title">{{ shortcut.title }}</div>
              <div style="font-size: 12px; color: #6b7280; margin-top: 2px;">
                {{ shortcut.content.substring(0, 40) }}{{ shortcut.content.length > 40 ? '...' : '' }}
              </div>
            </div>
            <div class="shortcut-trigger">{{ shortcut.trigger }}</div>
          </div>

          <div v-if="shortcuts.length > 8" style="text-align: center; margin-top: 12px;">
            <button @click="openDashboard" style="background: #667eea; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-size: 12px; cursor: pointer;">
              Ver todos ({{ shortcuts.length }})
            </button>
          </div>
        </div>

        <div v-else style="text-align: center; padding: 20px; color: #6b7280;">
          <div style="margin-bottom: 12px;">Nenhum atalho encontrado</div>
          <button @click="openDashboard" style="background: #667eea; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-size: 12px; cursor: pointer;">
            Criar primeiro atalho
          </button>
        </div>

        <!-- Sync Info -->
        <div style="text-align: center; margin-top: 16px; padding-top: 16px; border-top: 1px solid #e5e7eb;">
          <button @click="syncShortcuts" :disabled="syncing" style="background: #10b981; color: white; border: none; padding: 6px 12px; border-radius: 6px; font-size: 11px; cursor: pointer;">
            <span v-if="syncing">Sincronizando...</span>
            <span v-else>🔄 Sincronizar</span>
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
        // Verificar se há token armazenado
        const result = await chrome.storage.local.get(['token', 'user'])
        
        if (result.token && result.user) {
          this.isAuthenticated = true
          this.user = result.user
          await this.loadShortcuts()
        }
      } catch (error) {
        console.error('Erro ao verificar autenticação:', error)
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
        }
      } catch (error) {
        console.error('Erro ao carregar atalhos:', error)
      }
    },

    async syncShortcuts() {
      this.syncing = true
      
      try {
        const response = await chrome.runtime.sendMessage({ type: 'SYNC_SHORTCUTS' })
        
        if (response.success) {
          this.shortcuts = response.shortcuts || []
          this.success = 'Atalhos sincronizados!'
          
          setTimeout(() => {
            this.success = null
          }, 2000)
        } else {
          this.error = 'Erro na sincronização'
        }
      } catch (error) {
        console.error('Erro na sincronização:', error)
        this.error = 'Erro de conexão'
      } finally {
        this.syncing = false
      }
    },

    openDashboard() {
      chrome.tabs.create({ url: 'http://127.0.0.1:8000/dashboard/' })
    }
  }
}
</script>
