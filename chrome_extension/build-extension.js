#!/usr/bin/env node

/**
 * Script de build personalizado para a extensão Chrome Symplifika
 * Garante que todos os arquivos necessários sejam copiados para dist/
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

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

function copyFile(src, dest) {
    try {
        const destDir = path.dirname(dest);
        if (!fs.existsSync(destDir)) {
            fs.mkdirSync(destDir, { recursive: true });
        }
        fs.copyFileSync(src, dest);
        log(`✅ Copiado: ${src} → ${dest}`, 'green');
        return true;
    } catch (error) {
        log(`❌ Erro ao copiar ${src}: ${error.message}`, 'red');
        return false;
    }
}

function copyDirectory(src, dest) {
    try {
        if (!fs.existsSync(dest)) {
            fs.mkdirSync(dest, { recursive: true });
        }
        
        const files = fs.readdirSync(src);
        let copiedCount = 0;
        
        files.forEach(file => {
            const srcPath = path.join(src, file);
            const destPath = path.join(dest, file);
            
            if (fs.statSync(srcPath).isDirectory()) {
                copyDirectory(srcPath, destPath);
            } else {
                if (copyFile(srcPath, destPath)) {
                    copiedCount++;
                }
            }
        });
        
        log(`✅ Diretório copiado: ${src} → ${dest} (${copiedCount} arquivos)`, 'green');
        return true;
    } catch (error) {
        log(`❌ Erro ao copiar diretório ${src}: ${error.message}`, 'red');
        return false;
    }
}

function main() {
    log('🚀 INICIANDO BUILD DA EXTENSÃO SYMPLIFIKA', 'bold');
    log('=' * 50, 'blue');
    
    try {
        // 1. Executar webpack build
        log('\n📦 Executando webpack build...', 'blue');
        execSync('npm run build', { stdio: 'inherit' });
        log('✅ Webpack build concluído', 'green');
        
        // 2. Verificar se dist existe
        const distPath = path.join(__dirname, 'dist');
        if (!fs.existsSync(distPath)) {
            fs.mkdirSync(distPath, { recursive: true });
            log('📁 Pasta dist/ criada', 'yellow');
        }
        
        // 3. Copiar manifest.json
        log('\n📋 Copiando arquivos essenciais...', 'blue');
        const manifestSrc = path.join(__dirname, 'manifest.json');
        const manifestDest = path.join(distPath, 'manifest.json');
        
        if (fs.existsSync(manifestSrc)) {
            copyFile(manifestSrc, manifestDest);
        } else {
            log('❌ manifest.json não encontrado!', 'red');
            process.exit(1);
        }
        
        // 4. Copiar ícones
        const iconsSrc = path.join(__dirname, 'icons');
        const iconsDest = path.join(distPath, 'icons');
        
        if (fs.existsSync(iconsSrc)) {
            copyDirectory(iconsSrc, iconsDest);
        } else {
            log('⚠️ Pasta icons/ não encontrada', 'yellow');
        }
        
        // 5. Verificar arquivos essenciais
        log('\n🔍 Verificando arquivos essenciais...', 'blue');
        const essentialFiles = [
            'manifest.json',
            'popup.html',
            'popup.js',
            'background.js',
            'content.js'
        ];
        
        let allFilesPresent = true;
        essentialFiles.forEach(file => {
            const filePath = path.join(distPath, file);
            if (fs.existsSync(filePath)) {
                const stats = fs.statSync(filePath);
                const size = (stats.size / 1024).toFixed(1);
                log(`✅ ${file} (${size} KB)`, 'green');
            } else {
                log(`❌ ${file} - FALTANDO!`, 'red');
                allFilesPresent = false;
            }
        });
        
        // 6. Verificar ícones
        const iconSizes = [16, 32, 48, 128];
        iconSizes.forEach(size => {
            const iconPath = path.join(iconsDest, `icon${size}.png`);
            if (fs.existsSync(iconPath)) {
                log(`✅ icon${size}.png`, 'green');
            } else {
                log(`⚠️ icon${size}.png - faltando`, 'yellow');
            }
        });
        
        // 7. Resultado final
        log('\n📊 RESULTADO DO BUILD', 'bold');
        log('=' * 30, 'blue');
        
        if (allFilesPresent) {
            log('🎉 BUILD CONCLUÍDO COM SUCESSO!', 'green');
            log('\n📝 Próximos passos:', 'blue');
            log('1. Abrir chrome://extensions/', 'blue');
            log('2. Ativar "Modo do desenvolvedor"', 'blue');
            log('3. Clicar "Carregar sem compactação"', 'blue');
            log('4. Selecionar a pasta: chrome_extension/dist/', 'blue');
            log('\n🎯 Pasta da extensão:', 'blue');
            log(distPath, 'yellow');
        } else {
            log('❌ BUILD INCOMPLETO - Arquivos faltando', 'red');
            process.exit(1);
        }
        
    } catch (error) {
        log(`❌ Erro durante o build: ${error.message}`, 'red');
        process.exit(1);
    }
}

main();
