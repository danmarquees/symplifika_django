#!/usr/bin/env node

// Script de Verificação Completa - Symplifika Chrome Extension
// Verifica todos os componentes necessários para funcionamento da extensão

console.log("🔍 VERIFICAÇÃO COMPLETA - SYMPLIFIKA CHROME EXTENSION");
console.log("=".repeat(70));
console.log("📅 Data:", new Date().toLocaleString("pt-BR"));
console.log("");

const fs = require("fs");
const path = require("path");

// Configurações
const API_BASE_URL = "http://127.0.0.1:8000";
const TEST_CREDENTIALS = {
  login: "admin",
  password: "admin",
};

let testResults = {
  passed: 0,
  failed: 0,
  warnings: 0,
  details: [],
};

// Função auxiliar para registrar resultado
function logTest(name, status, message, isWarning = false) {
  const statusIcon = status ? "✅" : isWarning ? "⚠️" : "❌";
  const statusText = status ? "PASSOU" : isWarning ? "AVISO" : "FALHOU";

  console.log(`${statusIcon} ${name}: ${statusText}`);
  if (message) console.log(`   ${message}`);

  testResults.details.push({ name, status, message, isWarning });

  if (status) {
    testResults.passed++;
  } else if (isWarning) {
    testResults.warnings++;
  } else {
    testResults.failed++;
  }
}

// Função para fazer requisição HTTP
async function makeRequest(url, options = {}) {
  try {
    const response = await fetch(url, {
      timeout: 10000,
      ...options,
      headers: {
        "Content-Type": "application/json",
        Origin: "chrome-extension://test",
        ...options.headers,
      },
    });

    let data;
    try {
      const text = await response.text();
      data = text ? JSON.parse(text) : null;
    } catch (e) {
      data = text;
    }

    return { success: response.ok, status: response.status, data };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

// Teste 1: Verificar arquivos da extensão
function testExtensionFiles() {
  console.log("\n1️⃣ VERIFICANDO ARQUIVOS DA EXTENSÃO");
  console.log("-".repeat(50));

  const requiredFiles = [
    { path: "dist/manifest.json", name: "Manifest" },
    { path: "dist/background.js", name: "Background Script" },
    { path: "dist/content.js", name: "Content Script" },
    { path: "dist/popup.html", name: "Popup HTML" },
    { path: "dist/popup.js", name: "Popup Script" },
    { path: "dist/icons", name: "Ícones", isDir: true },
  ];

  let allFilesOk = true;

  requiredFiles.forEach((file) => {
    const fullPath = path.join(__dirname, file.path);
    const exists = file.isDir
      ? fs.existsSync(fullPath) && fs.statSync(fullPath).isDirectory()
      : fs.existsSync(fullPath) && fs.statSync(fullPath).isFile();

    if (exists) {
      const size = file.isDir
        ? "diretório"
        : `${Math.round(fs.statSync(fullPath).size / 1024)}KB`;
      logTest(file.name, true, `${file.path} (${size})`);
    } else {
      logTest(file.name, false, `${file.path} não encontrado`);
      allFilesOk = false;
    }
  });

  return allFilesOk;
}

// Teste 2: Verificar manifest.json
function testManifest() {
  console.log("\n2️⃣ VERIFICANDO MANIFEST.JSON");
  console.log("-".repeat(50));

  try {
    const manifestPath = path.join(__dirname, "dist/manifest.json");
    const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));

    logTest(
      "Manifest Version",
      manifest.manifest_version === 3,
      `v${manifest.manifest_version}`,
    );
    logTest("Nome da Extensão", !!manifest.name, manifest.name);
    logTest("Versão", !!manifest.version, manifest.version);
    logTest(
      "Permissões",
      Array.isArray(manifest.permissions),
      `${manifest.permissions?.length || 0} permissões`,
    );
    logTest(
      "Background Script",
      !!manifest.background?.service_worker,
      manifest.background?.service_worker,
    );
    logTest(
      "Content Scripts",
      Array.isArray(manifest.content_scripts),
      `${manifest.content_scripts?.length || 0} scripts`,
    );
    logTest(
      "Action Popup",
      !!manifest.action?.default_popup,
      manifest.action?.default_popup,
    );

    return true;
  } catch (error) {
    logTest("Leitura do Manifest", false, `Erro: ${error.message}`);
    return false;
  }
}

// Teste 3: Verificar servidor Django
async function testDjangoServer() {
  console.log("\n3️⃣ VERIFICANDO SERVIDOR DJANGO");
  console.log("-".repeat(50));

  // Teste básico do servidor
  const serverTest = await makeRequest(`${API_BASE_URL}/`);
  if (serverTest.success) {
    logTest("Servidor Básico", true, `Status ${serverTest.status}`);
  } else {
    logTest(
      "Servidor Básico",
      false,
      serverTest.error || "Servidor não responde",
    );
    return false;
  }

  // Teste de CORS
  const corsTest = await makeRequest(`${API_BASE_URL}/api/token/`, {
    method: "OPTIONS",
  });
  logTest("Configuração CORS", corsTest.success, `Status ${corsTest.status}`);

  return true;
}

// Teste 4: Verificar autenticação
async function testAuthentication() {
  console.log("\n4️⃣ VERIFICANDO AUTENTICAÇÃO");
  console.log("-".repeat(50));

  // Teste com credenciais inválidas (deve retornar erro)
  const invalidTest = await makeRequest(`${API_BASE_URL}/api/token/`, {
    method: "POST",
    body: JSON.stringify({ login: "invalid", password: "invalid" }),
  });

  if (invalidTest.status === 400 || invalidTest.status === 401) {
    logTest(
      "Endpoint Auth",
      true,
      "Rejeita credenciais inválidas corretamente",
    );
  } else {
    logTest("Endpoint Auth", false, `Status inesperado: ${invalidTest.status}`);
    return null;
  }

  // Teste com credenciais válidas
  const validTest = await makeRequest(`${API_BASE_URL}/api/token/`, {
    method: "POST",
    body: JSON.stringify(TEST_CREDENTIALS),
  });

  if (validTest.success && validTest.data?.access) {
    logTest("Login Válido", true, "Token JWT obtido com sucesso");
    return validTest.data.access;
  } else {
    logTest("Login Válido", false, validTest.data?.error || "Falha no login");
    return null;
  }
}

// Teste 5: Verificar API de atalhos
async function testShortcutsAPI(token) {
  console.log("\n5️⃣ VERIFICANDO API DE ATALHOS");
  console.log("-".repeat(50));

  if (!token) {
    logTest("Token Necessário", false, "Token não disponível para testes");
    return false;
  }

  // Teste de listagem de atalhos
  const shortcutsTest = await makeRequest(
    `${API_BASE_URL}/shortcuts/api/shortcuts/`,
    {
      method: "GET",
      headers: { Authorization: `Bearer ${token}` },
    },
  );

  if (shortcutsTest.success) {
    const shortcuts = Array.isArray(shortcutsTest.data)
      ? shortcutsTest.data
      : shortcutsTest.data?.results || [];
    logTest(
      "Listagem de Atalhos",
      true,
      `${shortcuts.length} atalhos encontrados`,
    );

    // Verificar estrutura dos atalhos
    if (shortcuts.length > 0) {
      const firstShortcut = shortcuts[0];
      const hasRequiredFields = ["id", "trigger", "content", "is_active"].every(
        (field) => firstShortcut.hasOwnProperty(field),
      );
      logTest(
        "Estrutura dos Atalhos",
        hasRequiredFields,
        "Campos obrigatórios presentes",
      );

      // Mostrar alguns atalhos
      shortcuts.slice(0, 3).forEach((shortcut, index) => {
        console.log(
          `   📝 ${shortcut.trigger}: ${shortcut.content.substring(0, 40)}...`,
        );
      });
    } else {
      logTest(
        "Atalhos Disponíveis",
        false,
        "Nenhum atalho encontrado para teste",
        true,
      );
    }

    return shortcuts.length > 0;
  } else {
    logTest(
      "Listagem de Atalhos",
      false,
      shortcutsTest.error || `Status ${shortcutsTest.status}`,
    );
    return false;
  }
}

// Teste 6: Verificar perfil do usuário
async function testUserProfile(token) {
  console.log("\n6️⃣ VERIFICANDO PERFIL DO USUÁRIO");
  console.log("-".repeat(50));

  if (!token) {
    logTest("Token Necessário", false, "Token não disponível para testes");
    return false;
  }

  const profileTest = await makeRequest(`${API_BASE_URL}/api/profile/`, {
    method: "GET",
    headers: { Authorization: `Bearer ${token}` },
  });

  if (profileTest.success && profileTest.data) {
    const user = profileTest.data;
    logTest(
      "Perfil do Usuário",
      true,
      `Usuário: ${user.username || user.email}`,
    );

    console.log(`   👤 Username: ${user.username || "N/A"}`);
    console.log(`   📧 Email: ${user.email || "N/A"}`);
    console.log(
      `   👨‍💼 Nome: ${user.first_name || "N/A"} ${user.last_name || ""}`,
    );

    return true;
  } else {
    logTest(
      "Perfil do Usuário",
      false,
      profileTest.error || `Status ${profileTest.status}`,
    );
    return false;
  }
}

// Teste 7: Verificar dependências Node.js
function testNodeDependencies() {
  console.log("\n7️⃣ VERIFICANDO DEPENDÊNCIAS NODE.JS");
  console.log("-".repeat(50));

  try {
    const packagePath = path.join(__dirname, "package.json");
    const packageJson = JSON.parse(fs.readFileSync(packagePath, "utf8"));

    logTest(
      "Package.json",
      true,
      `${packageJson.name} v${packageJson.version}`,
    );

    // Verificar node_modules
    const nodeModulesPath = path.join(__dirname, "node_modules");
    const nodeModulesExists = fs.existsSync(nodeModulesPath);
    logTest(
      "Node Modules",
      nodeModulesExists,
      nodeModulesExists ? "Dependências instaladas" : "Execute npm install",
    );

    // Verificar algumas dependências críticas
    const criticalDeps = ["vue", "webpack", "vue-loader"];
    criticalDeps.forEach((dep) => {
      const depPath = path.join(__dirname, "node_modules", dep);
      const exists = fs.existsSync(depPath);
      logTest(`Dependência ${dep}`, exists, exists ? "OK" : "Faltando");
    });

    return nodeModulesExists;
  } catch (error) {
    logTest("Package.json", false, `Erro: ${error.message}`);
    return false;
  }
}

// Função principal
async function runAllTests() {
  console.log("🚀 Iniciando verificação completa...\n");

  const filesOk = testExtensionFiles();
  const manifestOk = testManifest();
  const serverOk = await testDjangoServer();
  const token = serverOk ? await testAuthentication() : null;
  const shortcutsOk = await testShortcutsAPI(token);
  const profileOk = await testUserProfile(token);
  const depsOk = testNodeDependencies();

  // Resumo final
  console.log("\n" + "=".repeat(70));
  console.log("📊 RESUMO DA VERIFICAÇÃO");
  console.log("=".repeat(70));

  console.log(`✅ Testes passaram: ${testResults.passed}`);
  console.log(`❌ Testes falharam: ${testResults.failed}`);
  console.log(`⚠️ Avisos: ${testResults.warnings}`);

  const totalTests =
    testResults.passed + testResults.failed + testResults.warnings;
  const successRate = Math.round((testResults.passed / totalTests) * 100);
  console.log(`📈 Taxa de sucesso: ${successRate}%`);

  // Status geral
  console.log("\n🎯 STATUS GERAL:");
  if (testResults.failed === 0) {
    console.log("🟢 TUDO FUNCIONANDO PERFEITAMENTE!");
    console.log("✅ A extensão está pronta para uso");

    console.log("\n📋 PRÓXIMOS PASSOS:");
    console.log("1. Abrir Chrome: chrome://extensions/");
    console.log('2. Ativar "Modo do desenvolvedor"');
    console.log("3. Carregar extensão da pasta: chrome_extension/dist/");
    console.log("4. Fazer login com: admin / admin");
    console.log("5. Testar atalhos: !ola, !email, !data, !assinatura");
  } else if (testResults.failed <= 2) {
    console.log("🟡 QUASE PRONTO - PEQUENOS AJUSTES NECESSÁRIOS");
    console.log("⚠️ Alguns componentes precisam de atenção");
  } else {
    console.log("🔴 PROBLEMAS CRÍTICOS ENCONTRADOS");
    console.log("❌ Correções necessárias antes do uso");
  }

  // Problemas encontrados
  const failures = testResults.details.filter((t) => !t.status && !t.isWarning);
  if (failures.length > 0) {
    console.log("\n🛠️ PROBLEMAS A CORRIGIR:");
    failures.forEach((failure) => {
      console.log(`❌ ${failure.name}: ${failure.message}`);
    });

    console.log("\n💡 SOLUÇÕES SUGERIDAS:");
    if (
      failures.some(
        (f) => f.name.includes("Arquivo") || f.name.includes("Manifest"),
      )
    ) {
      console.log("- Execute: npm run build");
    }
    if (
      failures.some(
        (f) => f.name.includes("Servidor") || f.name.includes("Auth"),
      )
    ) {
      console.log(
        "- Inicie o servidor: python manage.py runserver 127.0.0.1:8000",
      );
    }
    if (failures.some((f) => f.name.includes("Dependência"))) {
      console.log("- Instale dependências: npm install");
    }
  }

  // Avisos
  const warnings = testResults.details.filter((t) => t.isWarning);
  if (warnings.length > 0) {
    console.log("\n⚠️ AVISOS:");
    warnings.forEach((warning) => {
      console.log(`⚠️ ${warning.name}: ${warning.message}`);
    });
  }

  console.log("\n" + "=".repeat(70));
  console.log(
    `🏁 Verificação concluída em ${new Date().toLocaleTimeString("pt-BR")}`,
  );
  console.log("=".repeat(70));

  // Código de saída
  process.exit(testResults.failed > 0 ? 1 : 0);
}

// Executar testes
runAllTests().catch((error) => {
  console.error("\n❌ Erro durante verificação:", error);
  console.log("\n🐛 Por favor, reporte este erro com os detalhes acima.");
  process.exit(1);
});
