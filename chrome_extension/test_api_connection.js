// Script de teste para verificar conexão com API
const API_BASE_URL = 'http://127.0.0.1:8000'

async function testAPIConnection() {
  console.log('🔍 Testando conexão com API Symplifika...')
  
  try {
    // Teste 1: Verificar se servidor está respondendo
    console.log('\n1. Testando conexão básica...')
    const healthResponse = await fetch(`${API_BASE_URL}/`, {
      method: 'GET',
      headers: {
        'Origin': 'chrome-extension://test'
      }
    })
    console.log(`✅ Servidor respondeu: ${healthResponse.status}`)
    
    // Teste 2: Testar endpoint de token
    console.log('\n2. Testando endpoint de autenticação...')
    const tokenResponse = await fetch(`${API_BASE_URL}/api/token/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Origin': 'chrome-extension://test'
      },
      body: JSON.stringify({
        login: 'test',
        password: 'test123'
      })
    })
    
    const tokenData = await tokenResponse.json()
    console.log(`Status: ${tokenResponse.status}`)
    console.log('Resposta:', tokenData)
    
    if (tokenResponse.ok && tokenData.access) {
      console.log('✅ Autenticação funcionando!')
      
      // Teste 3: Testar endpoint de shortcuts
      console.log('\n3. Testando endpoint de shortcuts...')
      const shortcutsResponse = await fetch(`${API_BASE_URL}/shortcuts/api/shortcuts/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${tokenData.access}`,
          'Content-Type': 'application/json',
          'Origin': 'chrome-extension://test'
        }
      })
      
      const shortcutsData = await shortcutsResponse.json()
      console.log(`Status: ${shortcutsResponse.status}`)
      console.log('Atalhos encontrados:', shortcutsData.results?.length || 0)
      
      if (shortcutsResponse.ok) {
        console.log('✅ API de shortcuts funcionando!')
      } else {
        console.log('❌ Erro na API de shortcuts:', shortcutsData)
      }
    } else {
      console.log('❌ Falha na autenticação:', tokenData)
    }
    
  } catch (error) {
    console.error('❌ Erro na conexão:', error)
  }
}

// Executar teste se estiver no Node.js
if (typeof require !== 'undefined') {
  // Para Node.js, usar fetch polyfill
  const fetch = require('node-fetch')
  testAPIConnection()
} else {
  // Para browser, executar diretamente
  testAPIConnection()
}
