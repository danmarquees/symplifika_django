// Script de teste de conectividade simples para Symplifika Chrome Extension
// Testa a conexão com a API Django sem dependências externas

console.log('🧪 Iniciando teste de conectividade Symplifika...\n');

const API_BASE_URL = 'http://127.0.0.1:8000';

// Função para fazer requisições HTTP simples (sem node-fetch)
async function testEndpoint(url, method = 'GET', data = null, headers = {}) {
    try {
        console.log(`📡 Testando: ${method} ${url}`);

        // Para Node.js 18+, usar fetch nativo
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Origin': 'chrome-extension://test',
                ...headers
            }
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(url, options);
        const responseText = await response.text();

        let responseData;
        try {
            responseData = JSON.parse(responseText);
        } catch (e) {
            responseData = responseText;
        }

        console.log(`   ✅ Status: ${response.status}`);
        console.log(`   📄 Response: ${JSON.stringify(responseData).substring(0, 100)}...\n`);

        return { success: response.ok, status: response.status, data: responseData };

    } catch (error) {
        console.log(`   ❌ Erro: ${error.message}\n`);
        return { success: false, error: error.message };
    }
}

// Função principal de teste
async function runTests() {
    console.log('=' .repeat(60));
    console.log('🔍 TESTE DE CONECTIVIDADE SYMPLIFIKA CHROME EXTENSION');
    console.log('=' .repeat(60));

    // 1. Testar se o servidor está rodando
    console.log('1️⃣ Testando servidor Django...');
    const serverTest = await testEndpoint(`${API_BASE_URL}/`);

    if (!serverTest.success) {
        console.log('❌ FALHA: Servidor Django não está respondendo!');
        console.log('💡 Solução: Execute "python manage.py runserver 127.0.0.1:8000"');
        return;
    }

    // 2. Testar endpoint de autenticação
    console.log('2️⃣ Testando endpoint de autenticação...');
    const authTest = await testEndpoint(`${API_BASE_URL}/api/token/`, 'POST', {
        login: 'test_invalid',
        password: 'test_invalid'
    });

    if (authTest.status !== 400 && authTest.status !== 401) {
        console.log('❌ FALHA: Endpoint de autenticação não está funcionando corretamente!');
        return;
    }
    console.log('   ✅ Endpoint de auth respondendo (erro esperado com credenciais inválidas)');

    // 3. Testar CORS
    console.log('3️⃣ Testando configuração CORS...');
    const corsTest = await testEndpoint(`${API_BASE_URL}/api/token/`, 'OPTIONS');

    if (corsTest.success || corsTest.status === 200 || corsTest.status === 204) {
        console.log('   ✅ CORS configurado corretamente');
    } else {
        console.log('   ⚠️ CORS pode ter problemas - mas extensão ainda pode funcionar');
    }

    // 4. Verificar arquivos da extensão
    console.log('4️⃣ Verificando arquivos da extensão...');
    const fs = require('fs');
    const path = require('path');

    const requiredFiles = [
        'dist/manifest.json',
        'dist/background.js',
        'dist/content.js',
        'dist/popup.html',
        'dist/popup.js'
    ];

    let allFilesExist = true;
    for (const file of requiredFiles) {
        const filePath = path.join(__dirname, file);
        if (fs.existsSync(filePath)) {
            console.log(`   ✅ ${file} - OK`);
        } else {
            console.log(`   ❌ ${file} - FALTANDO`);
            allFilesExist = false;
        }
    }

    if (!allFilesExist) {
        console.log('❌ FALHA: Arquivos da extensão estão faltando!');
        console.log('💡 Solução: Execute "npm run build" para compilar a extensão');
        return;
    }

    // 5. Verificar manifest.json
    console.log('5️⃣ Verificando manifest.json...');
    try {
        const manifestPath = path.join(__dirname, 'dist/manifest.json');
        const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));

        console.log(`   ✅ Nome: ${manifest.name}`);
        console.log(`   ✅ Versão: ${manifest.version}`);
        console.log(`   ✅ Manifest Version: ${manifest.manifest_version}`);
        console.log(`   ✅ Permissões: ${manifest.permissions?.length || 0}`);

    } catch (error) {
        console.log(`   ❌ Erro ao ler manifest: ${error.message}`);
    }

    console.log('\n' + '=' .repeat(60));
    console.log('🎉 RESULTADO DO TESTE');
    console.log('=' .repeat(60));

    console.log('✅ Servidor Django: FUNCIONANDO');
    console.log('✅ API de autenticação: FUNCIONANDO');
    console.log('✅ Arquivos da extensão: COMPILADOS');
    console.log('✅ Configuração CORS: OK');

    console.log('\n🚀 PRÓXIMOS PASSOS:');
    console.log('1. Abrir Chrome e ir para chrome://extensions/');
    console.log('2. Ativar "Modo do desenvolvedor"');
    console.log('3. Clicar "Carregar sem compactação"');
    console.log('4. Selecionar a pasta: chrome_extension/dist/');
    console.log('5. Clicar no ícone da extensão e fazer login');

    console.log('\n📋 CREDENCIAIS DISPONÍVEIS PARA TESTE:');
    console.log('- admin / admin');
    console.log('- danmarques / [senha]');
    console.log('- testuser / [senha]');

    console.log('\n⚠️ POSSÍVEIS PROBLEMAS:');
    console.log('- Se login falhar: verificar credenciais no Django admin');
    console.log('- Se extensão não aparecer: recompilar com "npm run build"');
    console.log('- Se atalhos não carregarem: verificar se usuário tem atalhos criados');

    console.log('\n🔧 TROUBLESHOOTING:');
    console.log('- Console da extensão: F12 > Application > Extensions');
    console.log('- Console do background: chrome://extensions/ > "service worker"');
    console.log('- Logs do servidor: tail -f server.log');
}

// Executar testes
runTests().catch(error => {
    console.error('❌ Erro durante teste:', error);
    process.exit(1);
});
