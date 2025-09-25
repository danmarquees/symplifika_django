#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('🚀 Iniciando build da extensão Symplifika...');

// Verificar se os arquivos fonte existem
const requiredFiles = [
  'src/popup/App.vue',
  'src/background/background.js',
  'src/content/content.js',
  'src/manifest.json'
];

console.log('📋 Verificando arquivos fonte...');
for (const file of requiredFiles) {
  const filePath = path.join(__dirname, file);
  if (!fs.existsSync(filePath)) {
    console.error(`❌ Arquivo não encontrado: ${file}`);
    process.exit(1);
  }
  console.log(`✅ ${file}`);
}

// Criar diretório dist se não existir
const distDir = path.join(__dirname, 'dist');
if (!fs.existsSync(distDir)) {
  fs.mkdirSync(distDir, { recursive: true });
  console.log('📁 Diretório dist criado');
}

try {
  // Copiar manifest.json
  console.log('📄 Copiando manifest.json...');
  fs.copyFileSync(
    path.join(__dirname, 'src/manifest.json'),
    path.join(distDir, 'manifest.json')
  );

  // Copiar background script
  console.log('🔧 Copiando background script...');
  fs.copyFileSync(
    path.join(__dirname, 'src/background/background.js'),
    path.join(distDir, 'background.js')
  );

  // Copiar content script
  console.log('📝 Copiando content script...');
  fs.copyFileSync(
    path.join(__dirname, 'src/content/content.js'),
    path.join(distDir, 'content.js')
  );

  // Copiar popup HTML
  console.log('🎨 Copiando popup HTML...');
  fs.copyFileSync(
    path.join(__dirname, 'src/popup/popup.html'),
    path.join(distDir, 'popup.html')
  );

  // Processar App.vue (extrair template, script e style)
  console.log('⚙️ Processando App.vue...');
  const appVueContent = fs.readFileSync(path.join(__dirname, 'src/popup/App.vue'), 'utf8');
  
  // Extrair script
  const scriptMatch = appVueContent.match(/<script>([\s\S]*?)<\/script>/);
  if (scriptMatch) {
    const scriptContent = scriptMatch[1]
      .replace('export default', 'const App =')
      .replace(/name: 'App',/, '');
    
    const jsContent = `
// Vue App Component
${scriptContent}

// Inicializar Vue
document.addEventListener('DOMContentLoaded', () => {
  const { createApp } = Vue;
  createApp(App).mount('#app');
});
`;
    
    fs.writeFileSync(path.join(distDir, 'popup.js'), jsContent);
  }

  // Extrair e copiar estilos
  const styleMatch = appVueContent.match(/<style[^>]*>([\s\S]*?)<\/style>/);
  if (styleMatch) {
    fs.writeFileSync(path.join(distDir, 'popup.css'), styleMatch[1]);
  }

  // Copiar ícones se existirem
  const iconsDir = path.join(__dirname, 'src/icons');
  if (fs.existsSync(iconsDir)) {
    console.log('🖼️ Copiando ícones...');
    const distIconsDir = path.join(distDir, 'icons');
    if (!fs.existsSync(distIconsDir)) {
      fs.mkdirSync(distIconsDir, { recursive: true });
    }
    
    const iconFiles = fs.readdirSync(iconsDir);
    for (const iconFile of iconFiles) {
      fs.copyFileSync(
        path.join(iconsDir, iconFile),
        path.join(distIconsDir, iconFile)
      );
    }
  }

  console.log('✅ Build concluído com sucesso!');
  console.log('📁 Arquivos gerados em:', distDir);
  
  // Listar arquivos gerados
  const distFiles = fs.readdirSync(distDir);
  console.log('📋 Arquivos gerados:');
  distFiles.forEach(file => {
    const filePath = path.join(distDir, file);
    const stats = fs.statSync(filePath);
    console.log(`   ${file} (${Math.round(stats.size / 1024)}KB)`);
  });

  console.log('\n🎯 Próximos passos:');
  console.log('1. Abrir Chrome e ir para chrome://extensions/');
  console.log('2. Ativar "Modo do desenvolvedor"');
  console.log('3. Clicar "Carregar sem compactação"');
  console.log(`4. Selecionar a pasta: ${distDir}`);
  console.log('5. Testar a extensão!');

} catch (error) {
  console.error('❌ Erro durante o build:', error.message);
  process.exit(1);
}
