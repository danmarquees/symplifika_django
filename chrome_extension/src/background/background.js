// Background Script para Symplifika Chrome Extension (Vue.js)
// Gerencia autenticação, sincronização e comunicação com API

const API_BASE_URL = 'http://127.0.0.1:8000'

// Estado da extensão
let extensionState = {
  isAuthenticated: false,
  user: null,
  token: null,
  shortcuts: [],
  lastSync: null
}

// Inicialização da extensão
chrome.runtime.onInstalled.addListener(async () => {
  console.log('🚀 Symplifika Extension instalada/atualizada')
  
  // Restaurar estado do storage
  await restoreState()
  
  // Configurar alarme de sincronização (a cada 30 minutos)
  if (chrome.alarms) {
    chrome.alarms.create('syncShortcuts', { periodInMinutes: 30 })
  }
})

// Restaurar estado do storage
async function restoreState() {
  try {
    const result = await chrome.storage.local.get(['token', 'user', 'shortcuts', 'lastSync'])
    
    if (result.token) {
      extensionState.token = result.token
      extensionState.isAuthenticated = true
    }
    
    if (result.user) {
      extensionState.user = result.user
    }
    
    if (result.shortcuts) {
      extensionState.shortcuts = result.shortcuts
    }
    
    if (result.lastSync) {
      extensionState.lastSync = result.lastSync
    }
    
    console.log('📦 Estado restaurado:', {
      authenticated: extensionState.isAuthenticated,
      user: extensionState.user?.username,
      shortcuts: extensionState.shortcuts?.length || 0
    })
  } catch (error) {
    console.error('❌ Erro ao restaurar estado:', error)
  }
}

// Salvar estado no storage
async function saveState() {
  try {
    await chrome.storage.local.set({
      token: extensionState.token,
      user: extensionState.user,
      shortcuts: extensionState.shortcuts,
      lastSync: extensionState.lastSync
    })
  } catch (error) {
    console.error('❌ Erro ao salvar estado:', error)
  }
}

// Listener para mensagens do popup e content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('📨 Mensagem recebida:', request.type)
  
  switch (request.type) {
    case 'LOGIN':
      handleLogin(request.payload).then(sendResponse)
      return true // Indica resposta assíncrona
      
    case 'LOGOUT':
      handleLogout().then(sendResponse)
      return true
      
    case 'GET_SHORTCUTS':
      sendResponse({
        success: true,
        shortcuts: extensionState.shortcuts,
        user: extensionState.user
      })
      break
      
    case 'SYNC_SHORTCUTS':
      syncShortcuts().then(sendResponse)
      return true
      
    case 'EXPAND_TEXT':
      handleTextExpansion(request.payload).then(sendResponse)
      return true
      
    default:
      sendResponse({ success: false, error: 'Tipo de mensagem desconhecido' })
  }
})

// Função de login
async function handleLogin(credentials) {
  try {
    console.log('🔐 Tentando login para:', credentials.login)
    
    const response = await fetch(`${API_BASE_URL}/api/token/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Origin': chrome.runtime.getURL('')
      },
      body: JSON.stringify({
        login: credentials.login,
        password: credentials.password
      })
    })
    
    const data = await response.json()
    
    if (response.ok && data.access) {
      // Login bem-sucedido
      extensionState.token = data.access
      extensionState.user = data.user
      extensionState.isAuthenticated = true
      
      // Salvar no storage
      await saveState()
      
      // Sincronizar atalhos
      await syncShortcuts()
      
      console.log('✅ Login realizado com sucesso:', extensionState.user.username)
      
      return {
        success: true,
        user: extensionState.user,
        token: extensionState.token
      }
    } else {
      console.error('❌ Erro no login:', data)
      return {
        success: false,
        error: data.error || data.detail || 'Credenciais inválidas'
      }
    }
  } catch (error) {
    console.error('❌ Erro de conexão no login:', error)
    return {
      success: false,
      error: 'Erro de conexão. Verifique se o servidor Django está rodando.'
    }
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
      shortcuts: [],
      lastSync: null
    }
    
    // Limpar storage
    await chrome.storage.local.clear()
    
    console.log('👋 Logout realizado')
    
    return { success: true }
  } catch (error) {
    console.error('❌ Erro no logout:', error)
    return { success: false, error: 'Erro no logout' }
  }
}

// Sincronizar atalhos com a API
async function syncShortcuts() {
  if (!extensionState.isAuthenticated || !extensionState.token) {
    return { success: false, error: 'Não autenticado' }
  }
  
  try {
    console.log('🔄 Sincronizando atalhos...')
    
    const response = await fetch(`${API_BASE_URL}/shortcuts/api/shortcuts/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${extensionState.token}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      extensionState.shortcuts = data.results || data || []
      extensionState.lastSync = new Date().toISOString()
      
      // Salvar no storage
      await saveState()
      
      console.log(`✅ ${extensionState.shortcuts.length} atalhos sincronizados`)
      
      return {
        success: true,
        shortcuts: extensionState.shortcuts,
        lastSync: extensionState.lastSync
      }
    } else {
      console.error('❌ Erro na sincronização:', response.status)
      return { success: false, error: 'Erro na API' }
    }
  } catch (error) {
    console.error('❌ Erro de conexão na sincronização:', error)
    return { success: false, error: 'Erro de conexão' }
  }
}

// Expandir texto com atalho
async function handleTextExpansion(payload) {
  const { trigger } = payload
  
  // Procurar atalho pelo trigger
  const shortcut = extensionState.shortcuts.find(s => 
    s.trigger === trigger && s.is_active
  )
  
  if (!shortcut) {
    return { success: false, error: 'Atalho não encontrado' }
  }
  
  try {
    // Processar template com variáveis
    let expandedText = shortcut.content
    
    // Variáveis básicas
    const now = new Date()
    const variables = {
      'user.name': extensionState.user?.first_name || extensionState.user?.username || '',
      'user.email': extensionState.user?.email || '',
      'date.today': now.toLocaleDateString('pt-BR'),
      'date.time': now.toLocaleTimeString('pt-BR'),
      'date.year': now.getFullYear().toString(),
      'date.month': (now.getMonth() + 1).toString().padStart(2, '0'),
      'date.day': now.getDate().toString().padStart(2, '0')
    }
    
    // Substituir variáveis
    for (const [key, value] of Object.entries(variables)) {
      const regex = new RegExp(`{{\\s*${key}\\s*}}`, 'g')
      expandedText = expandedText.replace(regex, value)
    }
    
    // Marcar como usado (opcional - não bloquear se falhar)
    try {
      await fetch(`${API_BASE_URL}/shortcuts/api/shortcuts/${shortcut.id}/use/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${extensionState.token}`,
          'Content-Type': 'application/json'
        }
      })
    } catch (error) {
      console.warn('⚠️ Não foi possível marcar atalho como usado:', error)
    }
    
    console.log('✨ Texto expandido:', trigger, '->', expandedText.substring(0, 50) + '...')
    
    return {
      success: true,
      expandedText: expandedText,
      shortcut: shortcut
    }
  } catch (error) {
    console.error('❌ Erro na expansão:', error)
    return { success: false, error: 'Erro na expansão' }
  }
}

// Alarme de sincronização automática
if (chrome.alarms) {
  chrome.alarms.onAlarm.addListener(async (alarm) => {
    if (alarm.name === 'syncShortcuts' && extensionState.isAuthenticated) {
      console.log('⏰ Sincronização automática iniciada')
      await syncShortcuts()
    }
  })
}

// Inicialização quando o service worker é ativado
chrome.runtime.onStartup.addListener(async () => {
  await restoreState()
  
  if (extensionState.isAuthenticated) {
    console.log('🔄 Sincronização na inicialização')
    await syncShortcuts()
  }
})

console.log('🎯 Background script carregado - Symplifika v2.0.0')
