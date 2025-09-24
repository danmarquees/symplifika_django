#!/usr/bin/env node

/**
 * Script de teste para verificar se a extensão Vue.js está funcionando
 */

const fs = require('fs');
const path = require('path');

// Cores para output
const colors = {
    green: '\x1b[32m',
    red: '\x1b[31m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    reset: '\x1b[0m',
    bold: '\x1b[1m'
};

function log(message, color = 'reset') {
    console.log(`${colors[color]}${message}${colors.reset}`);
}

function checkFile(filePath, description) {
    const exists = fs.existsSync(filePath);
    const status = exists ? '✅' : '❌';
    const color = exists ? 'green' : 'red';
    
    log(`${status} ${description}`, color);
    
    if (exists) {
        const stats = fs.statSync(filePath);
        const size = (stats.size / 1024).toFixed(1);
        log(`   📁 ${filePath} (${size} KB)`, 'blue');
    }
    
    return exists;
}

function checkDirectory(dirPath, description) {
    const exists = fs.existsSync(dirPath);
    const status = exists ? '✅' : '❌';
    const color = exists ? 'green' : 'red';
    
    log(`${status} ${description}`, color);
    
    if (exists) {
        const files = fs.readdirSync(dirPath);
        log(`   📁 ${dirPath} (${files.length} arquivos)`, 'blue');
    }
    
    return exists;
}

function main() {
    log('🧪 TESTE DA EXTENSÃO CHROME SYMPLIFIKA - VUE.JS', 'bold');
    log('=' * 60, 'blue');

    const distPath = path.join(__dirname, 'dist');
    const iconsPath = path.join(distPath, 'icons');

    // Verificar estrutura básica
    log('\n📦 Verificando estrutura da extensão...', 'blue');
    
    const checks = [
        [distPath, 'Pasta dist/ existe'],
        [path.join(distPath, 'manifest.json'), 'Manifest da extensão'],
        [path.join(distPath, 'popup.html'), 'Interface do popup'],
        [path.join(distPath, 'popup.js'), 'Vue.js app compilado'],
        [path.join(distPath, 'background.js'), 'Background script'],
        [path.join(distPath, 'content.js'), 'Content script'],
        [iconsPath, 'Pasta de ícones'],
        [path.join(iconsPath, 'icon16.png'), 'Ícone 16x16'],
        [path.join(iconsPath, 'icon32.png'), 'Ícone 32x32'],
        [path.join(iconsPath, 'icon48.png'), 'Ícone 48x48'],
        [path.join(iconsPath, 'icon128.png'), 'Ícone 128x128']
    ];

    let passedChecks = 0;
    
    checks.forEach(([filePath, description]) => {
        const isDir = description.includes('Pasta') || description.includes('pasta');
        const passed = isDir ? checkDirectory(filePath, description) : checkFile(filePath, description);
        if (passed) passedChecks++;
    });

    // Verificar conteúdo do manifest
    log('\n🔧 Verificando configuração do manifest...', 'blue');
    
    const manifestPath = path.join(distPath, 'manifest.json');
    if (fs.existsSync(manifestPath)) {
        try {
            const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
            
            const manifestChecks = [
                [manifest.manifest_version === 3, 'Manifest v3'],
                [manifest.name && manifest.name.includes('Symplifika'), 'Nome da extensão'],
                [manifest.version, 'Versão definida'],
                [manifest.permissions && manifest.permissions.length > 0, 'Permissões configuradas'],
                [manifest.action && manifest.action.default_popup, 'Popup configurado'],
                [manifest.background && manifest.background.service_worker, 'Service worker configurado'],
                [manifest.content_scripts && manifest.content_scripts.length > 0, 'Content scripts configurados']
            ];

            manifestChecks.forEach(([check, description]) => {
                const status = check ? '✅' : '❌';
                const color = check ? 'green' : 'red';
                log(`${status} ${description}`, color);
                if (check) passedChecks++;
            });

            // Mostrar informações do manifest
            log('\n📋 Informações do manifest:', 'yellow');
            log(`   Nome: ${manifest.name}`, 'blue');
            log(`   Versão: ${manifest.version}`, 'blue');
            log(`   Descrição: ${manifest.description}`, 'blue');
            log(`   Permissões: ${manifest.permissions.join(', ')}`, 'blue');

        } catch (error) {
            log('❌ Erro ao ler manifest.json', 'red');
            log(`   ${error.message}`, 'red');
        }
    }

    // Verificar tamanhos dos arquivos
    log('\n📊 Tamanhos dos arquivos:', 'blue');
    
    const filesToCheck = [
        'popup.js',
        'background.js', 
        'content.js',
        'popup.html',
        'manifest.json'
    ];

    filesToCheck.forEach(fileName => {
        const filePath = path.join(distPath, fileName);
        if (fs.existsSync(filePath)) {
            const stats = fs.statSync(filePath);
            const size = (stats.size / 1024).toFixed(1);
            const sizeColor = stats.size > 100000 ? 'yellow' : 'green'; // Avisar se > 100KB
            log(`   ${fileName}: ${size} KB`, sizeColor);
        }
    });

    // Resumo final
    log('\n📈 RESUMO DO TESTE', 'bold');
    log('=' * 20, 'blue');
    
    const totalChecks = checks.length + 7; // 7 checks do manifest
    const percentage = Math.round((passedChecks / totalChecks) * 100);
    
    log(`Verificações passaram: ${passedChecks}/${totalChecks} (${percentage}%)`, 
         percentage >= 90 ? 'green' : percentage >= 70 ? 'yellow' : 'red');

    if (percentage >= 90) {
        log('\n🎉 EXTENSÃO PRONTA PARA INSTALAÇÃO!', 'green');
        log('\n📝 Próximos passos:', 'blue');
        log('1. Abrir chrome://extensions/', 'blue');
        log('2. Ativar "Modo do desenvolvedor"', 'blue');
        log('3. Clicar "Carregar sem compactação"', 'blue');
        log('4. Selecionar a pasta: chrome_extension/dist/', 'blue');
        log('5. Testar login na extensão', 'blue');
    } else if (percentage >= 70) {
        log('\n⚠️  Extensão parcialmente pronta. Verificar erros acima.', 'yellow');
    } else {
        log('\n❌ Extensão com problemas. Corrigir erros antes de instalar.', 'red');
    }

    // Instruções de instalação
    log('\n🔗 Links úteis:', 'blue');
    log('• Chrome Extensions: chrome://extensions/', 'blue');
    log('• Django Dashboard: http://127.0.0.1:8000/dashboard/', 'blue');
    log('• Documentação: EXTENSAO_VUE_INSTALACAO.md', 'blue');
}

main();
