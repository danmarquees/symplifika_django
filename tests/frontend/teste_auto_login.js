#!/usr/bin/env node

// Script de teste para verificar se o login automático está funcionando
// Simula o comportamento da extensão Chrome

const API_BASE_URL = 'http://127.0.0.1:8000';

console.log('🧪 TESTE DE LOGIN AUTOMÁTICO - SYMPLIFIKA CHROME EXTENSION');
console.log('=' .repeat(70));
console.log('📅 Data:', new Date().toLocaleString('pt-BR'));
console.log('');

async function testAutoLoginAPI() {
    try {
        console.log('1️⃣ Testando endpoint de verificação de sessão...');

        const response = await fetch(`${API_BASE_URL}/users/api/auth/check-session/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Origin': 'chrome-extension://test-extension-id'
            },
            credentials: 'include'
        });

        console.log(`📡 Status: ${response.status} ${response.statusText}`);

        const data = await response.text();
        console.log('📄 Resposta raw:', data.substring(0, 200) + '...');

        let jsonData;
        try {
            jsonData = JSON.parse(data);
        } catch (e) {
            console.log('❌ Resposta não é JSON válido');
            return false;
        }

        console.log('📊 Dados estruturados:', JSON.stringify(jsonData, null, 2));

        if (response.status === 401) {
            console.log('ℹ️ Usuário não está logado na aplicação principal');
            console.log('💡 Para testar: faça login em http://127.0.0.1:8000/login/');
            return false;
        }

        if (response.status === 200 && jsonData.authenticated) {
            console.log('✅ Login automático funcionando!');
            console.log(`👤 Usuário: ${jsonData.user?.username || 'N/A'}`);
            console.log(`📧 Email: ${jsonData.user?.email || 'N/A'}`);
            console.log(`🔑 Token gerado: ${jsonData.access ? 'Sim' : 'Não'}`);
            return true;
        }

        console.log('⚠️ Resposta inesperada do servidor');
        return false;

    } catch (error) {
        console.error('❌ Erro no teste:', error.message);
        return false;
    }
}

async function testHeartbeatAPI() {
    try {
        console.log('\n2️⃣ Testando endpoint de heartbeat...');

        const response = await fetch(`${API_BASE_URL}/users/api/auth/extension-heartbeat/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Origin': 'chrome-extension://test-extension-id'
            }
        });

        console.log(`📡 Status: ${response.status} ${response.statusText}`);

        const jsonData = await response.json();
        console.log('📊 Heartbeat response:', JSON.stringify(jsonData, null, 2));

        if (jsonData.status === 'active') {
            console.log('✅ Heartbeat funcionando!');
            return true;
        }

        console.log('ℹ️ Heartbeat indica usuário não autenticado');
        return false;

    } catch (error) {
        console.error('❌ Erro no teste de heartbeat:', error.message);
        return false;
    }
}

async function testCORSConfiguration() {
    try {
        console.log('\n3️⃣ Testando configuração CORS...');

        const response = await fetch(`${API_BASE_URL}/users/api/auth/check-session/`, {
            method: 'OPTIONS',
            headers: {
                'Origin': 'chrome-extension://test-extension-id',
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'Content-Type'
            }
        });

        console.log(`📡 CORS preflight status: ${response.status}`);

        const corsHeaders = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
        };

        console.log('📊 Headers CORS:', corsHeaders);

        if (response.status === 200 || response.status === 204) {
            console.log('✅ CORS configurado corretamente para extensões Chrome');
            return true;
        }

        console.log('⚠️ Possíveis problemas de CORS');
        return false;

    } catch (error) {
        console.error('❌ Erro no teste de CORS:', error.message);
        return false;
    }
}

async function runAllTests() {
    console.log('🚀 Iniciando testes de login automático...\n');

    const results = {
        autoLogin: false,
        heartbeat: false,
        cors: false
    };

    // Teste 1: Auto-login
    results.autoLogin = await testAutoLoginAPI();

    // Teste 2: Heartbeat
    results.heartbeat = await testHeartbeatAPI();

    // Teste 3: CORS
    results.cors = await testCORSConfiguration();

    // Resumo
    console.log('\n' + '=' .repeat(70));
    console.log('📊 RESUMO DOS TESTES');
    console.log('=' .repeat(70));

    console.log(`✅ Auto-login API: ${results.autoLogin ? 'FUNCIONANDO' : 'FALHOU'}`);
    console.log(`✅ Heartbeat API: ${results.heartbeat ? 'FUNCIONANDO' : 'FALHOU'}`);
    console.log(`✅ CORS Config: ${results.cors ? 'FUNCIONANDO' : 'FALHOU'}`);

    const successCount = Object.values(results).filter(Boolean).length;
    const totalTests = Object.keys(results).length;

    console.log(`📈 Taxa de sucesso: ${Math.round((successCount / totalTests) * 100)}%`);

    if (successCount === totalTests) {
        console.log('\n🎉 TODOS OS TESTES PASSARAM!');
        console.log('✅ A funcionalidade de login automático está pronta');
        console.log('\n📋 COMO TESTAR NA EXTENSÃO:');
        console.log('1. Faça login na aplicação Django: http://127.0.0.1:8000/login/');
        console.log('2. Abra a extensão Chrome');
        console.log('3. A extensão deve fazer login automaticamente');
        console.log('4. Você deve ver a mensagem: "Bem-vindo! Login automático realizado."');
    } else {
        console.log('\n⚠️ ALGUNS TESTES FALHARAM');

        if (!results.autoLogin) {
            console.log('\n🔧 PARA CORRIGIR AUTO-LOGIN:');
            console.log('1. Verifique se o servidor Django está rodando');
            console.log('2. Faça login na aplicação web primeiro');
            console.log('3. Verifique se as URLs estão corretas');
        }

        if (!results.heartbeat) {
            console.log('\n🔧 PARA CORRIGIR HEARTBEAT:');
            console.log('1. Verifique se o endpoint foi adicionado às URLs');
            console.log('2. Teste manualmente: POST /users/api/auth/extension-heartbeat/');
        }

        if (!results.cors) {
            console.log('\n🔧 PARA CORRIGIR CORS:');
            console.log('1. Verifique as configurações CORS no Django');
            console.log('2. Certifique-se de que chrome-extension:// está permitido');
        }
    }

    console.log('\n🔍 LOGS DE DEBUG:');
    console.log('- Console da extensão: F12 > Application > Extensions');
    console.log('- Background script: chrome://extensions/ > "service worker"');
    console.log('- Logs do Django: tail -f server.log');

    console.log('\n' + '=' .repeat(70));
    console.log(`🏁 Testes concluídos em ${new Date().toLocaleTimeString('pt-BR')}`);
    console.log('=' .repeat(70));

    process.exit(successCount === totalTests ? 0 : 1);
}

// Executar testes
runAllTests().catch(error => {
    console.error('\n❌ Erro durante execução dos testes:', error);
    console.log('\n🐛 Detalhes do erro:');
    console.log(error.stack);
    process.exit(1);
});
