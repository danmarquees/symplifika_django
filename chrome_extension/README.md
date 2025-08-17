# Symplifika Chrome Extension

Extensão oficial do Symplifika para Google Chrome que permite expandir atalhos de texto automaticamente em qualquer site com inteligência artificial.

![Chrome Extension](https://img.shields.io/badge/chrome-extension-blue.svg)
![Version](https://img.shields.io/badge/version-1.0.0-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🚀 Funcionalidades

### ✨ Detecção Automática de Atalhos
- **Detecção em tempo real**: Identifica atalhos enquanto você digita
- **Padrão intuitivo**: Use `//palavra-chave` para ativar qualquer atalho
- **Expansão instantânea**: Substitui automaticamente o gatilho pelo conteúdo expandido
- **Compatível com todos os sites**: Funciona em qualquer campo de texto da web

### 🤖 Integração com IA
- **Expansão inteligente**: Atalhos expandidos automaticamente com OpenAI
- **Conteúdo dinâmico**: Suporte a variáveis que podem ser preenchidas em tempo real
- **Contexto preservado**: Mantém o contexto original ao expandir com IA

### 📱 Interface Moderna
- **Popup intuitivo**: Acesse rapidamente seus atalhos favoritos
- **Busca avançada**: Encontre atalhos por trigger, título ou conteúdo
- **Estatísticas em tempo real**: Veja quantos atalhos você tem e quantas vezes os usou
- **Tema responsivo**: Suporte a tema claro/escuro automático

### ⚙️ Configurações Avançadas
- **Conexão personalizável**: Configure a URL do seu servidor Symplifika
- **Comportamento ajustável**: Controle como e quando os atalhos são expandidos
- **Sincronização automática**: Mantenha seus atalhos sempre atualizados
- **Modo debug**: Para desenvolvedores e troubleshooting

## 📦 Instalação

### Pré-requisitos
- Google Chrome 88+ ou Chromium
- Servidor Symplifika rodando (backend Django)

### Método 1: Chrome Web Store (Recomendado)
1. Vá para a [Chrome Web Store](https://chrome.google.com/webstore)
2. Busque por "Symplifika"
3. Clique em "Adicionar ao Chrome"
4. Confirme a instalação

### Método 2: Instalação Manual (Desenvolvimento)
1. Baixe ou clone este repositório
2. Abra o Chrome e vá para `chrome://extensions/`
3. Ative o "Modo do desenvolvedor" no canto superior direito
4. Clique em "Carregar sem compactação"
5. Selecione a pasta `chrome_extension`

## 🔧 Configuração

### 1. Configuração Inicial
1. Clique no ícone da extensão na barra de ferramentas
2. Se não estiver logado, clique em "Fazer Login"
3. Configure a URL do seu servidor Symplifika (padrão: `http://localhost:8000`)
4. Faça login com suas credenciais

### 2. Configurações Avançadas
1. Clique com o botão direito no ícone da extensão
2. Selecione "Opções" ou clique no ícone de configurações no popup
3. Configure as preferências:
   - **URL do Servidor**: Endereço do seu backend Symplifika
   - **Expansão Automática**: Ativar/desativar expansão automática
   - **Notificações**: Mostrar feedback quando atalhos são usados
   - **Delay de Detecção**: Tempo de espera antes de detectar atalhos
   - **Intervalo de Sincronização**: Frequência de sincronização com o servidor

## 🎯 Como Usar

### Uso Básico
1. **Digite um atalho**: Em qualquer campo de texto, digite um gatilho como `//email-boasvindas`
2. **Pressione Tab ou Enter**: O atalho será automaticamente expandido
3. **Variáveis dinâmicas**: Se o atalho tiver variáveis, uma janela aparecerá para preenchê-las

### Atalhos de Teclado
- **Ctrl/Cmd + J**: Abrir busca rápida de atalhos (em desenvolvimento)
- **Tab ou Enter**: Expandir atalho detectado
- **Esc**: Cancelar expansão de atalho

### Pelo Popup
1. Clique no ícone da extensão
2. Busque pelo atalho desejado
3. Clique em "Usar Atalho" ou simplesmente clique no atalho
4. O conteúdo será copiado para a área de transferência

### Menu de Contexto
1. Selecione texto em qualquer página
2. Clique com o botão direito
3. Escolha "Expandir com Symplifika" (se disponível)

## 📊 Interface do Popup

### Dashboard
- **Estatísticas rápidas**: Número de atalhos, usos hoje, IA restante
- **Lista de atalhos**: Seus atalhos mais usados e recentes
- **Busca**: Campo de busca para encontrar atalhos rapidamente
- **Filtros**: Todos, Recentes, Favoritos

### Ações Disponíveis
- **Copiar**: Copia o conteúdo do atalho para a área de transferência
- **Usar**: Expande o atalho (com IA se necessário) e copia o resultado
- **Criar Atalho**: Abre o painel web para criar novos atalhos
- **Dashboard**: Abre o painel web principal

## ⚙️ Página de Configurações

### Seções Disponíveis

#### 🔗 Conexão
- URL do servidor Symplifika
- Timeout da API
- Teste de conexão

#### 👤 Conta
- Informações do usuário logado
- Plano atual e limitações
- Estatísticas de uso
- Opção de logout

#### 🎯 Comportamento
- Ativar/desativar extensão
- Expansão automática
- Notificações
- Efeitos sonoros
- Delay de detecção
- Intervalo de sincronização

#### 🔧 Avançado
- Modo debug
- Recursos beta
- Limpar cache
- Exportar/importar configurações

## 🔄 Sincronização

A extensão sincroniza automaticamente com o servidor Symplifika:

- **Sincronização automática**: A cada 30 minutos (configurável)
- **Sincronização manual**: Clique no botão de atualizar no popup
- **Sincronização no login**: Sempre que faz login
- **Cache local**: Atalhos ficam disponíveis mesmo offline

## 🎨 Personalização

### Temas
- **Tema automático**: Segue a preferência do sistema
- **Tema claro**: Interface clara para uso diurno
- **Tema escuro**: Interface escura para uso noturno

### Notificações
- **Toast notifications**: Feedback visual discreto
- **Indicadores de status**: Estados de sincronização
- **Contadores em tempo real**: Estatísticas atualizadas

## 🛠️ Desenvolvimento

### Estrutura do Projeto
```
chrome_extension/
├── manifest.json          # Configuração da extensão
├── background.js          # Service worker principal
├── content.js            # Script de detecção de atalhos
├── content.css           # Estilos para elementos injetados
├── popup.html            # Interface do popup
├── popup.js              # Lógica do popup
├── popup.css             # Estilos do popup
├── options.html          # Página de configurações
├── options.js            # Lógica das configurações
├── options.css           # Estilos das configurações
├── icons/                # Ícones da extensão
└── README.md             # Este arquivo
```

### Scripts Principais

#### Background Script (`background.js`)
- Gerencia comunicação com a API
- Armazena dados localmente
- Coordena entre content scripts e popup

#### Content Script (`content.js`)
- Detecta atalhos em tempo real
- Injeta interface de feedback
- Gerencia expansão de atalhos

#### Popup (`popup.js`)
- Interface principal do usuário
- Busca e filtragem de atalhos
- Ações rápidas

#### Options (`options.js`)
- Página de configurações completa
- Gerenciamento de conta
- Ferramentas avançadas

### APIs Utilizadas
- **Chrome Extensions API**: Funcionalidades da extensão
- **Chrome Storage API**: Armazenamento local
- **Fetch API**: Comunicação com servidor
- **Clipboard API**: Cópia para área de transferência

## 🐛 Solução de Problemas

### Problemas Comuns

#### Extensão não detecta atalhos
1. Verifique se a extensão está ativada
2. Confirme se está logado no servidor
3. Teste a conexão nas configurações
4. Verifique se os atalhos foram sincronizados

#### Erro de conexão
1. Confirme a URL do servidor nas configurações
2. Verifique se o servidor está rodando
3. Teste a conexão manualmente
4. Verifique configurações de CORS no servidor

#### Atalhos não expandem
1. Verifique se a expansão automática está ativada
2. Confirme se o gatilho está correto (deve começar com //)
3. Tente pressionar Tab ou Enter após o gatilho
4. Verifique se há erros no console (modo debug)

#### Problemas de sincronização
1. Force uma sincronização manual no popup
2. Verifique sua conexão com a internet
3. Confirme se está logado
4. Limpe o cache da extensão se necessário

### Debug

#### Ativar Modo Debug
1. Vá para as configurações da extensão
2. Ative "Modo Debug" na seção Avançado
3. Abra o Console do Desenvolvedor (F12)
4. Verifique os logs da extensão

#### Logs Úteis
- `Symplifika Background Service Worker loaded`
- `Symplifika Content Script iniciado`
- `Shortcut detected: //exemplo`
- `API response: {...}`

#### Ferramentas de Debug
- **chrome://extensions/**: Gerenciar extensões
- **Inspect views: background page**: Debug do service worker
- **Console**: Logs em tempo real
- **Network tab**: Requisições à API

## 🔒 Privacidade e Segurança

### Dados Coletados
- **Atalhos de texto**: Armazenados localmente e sincronizados com seu servidor
- **Estatísticas de uso**: Contadores anônimos para melhorar a experiência
- **Configurações**: Preferências pessoais armazenadas localmente

### Dados NÃO Coletados
- **Conteúdo digitado**: Não monitoramos o que você digita além dos atalhos
- **Dados pessoais**: Não acessamos informações pessoais do navegador
- **Histórico de navegação**: Não rastreamos quais sites você visita

### Segurança
- **Comunicação criptografada**: Todas as requisições usam HTTPS em produção
- **Armazenamento local**: Dados ficam apenas no seu computador
- **Token de autenticação**: Gerenciado de forma segura
- **Código aberto**: Código-fonte disponível para auditoria

## 📚 API Integration

### Endpoints Utilizados
```javascript
// Autenticação
POST /users/auth/login/
POST /users/auth/logout/

// Atalhos
GET /shortcuts/api/shortcuts/
POST /shortcuts/api/shortcuts/{id}/use/
POST /shortcuts/api/shortcuts/search/

// Usuário
GET /users/api/users/me/
GET /users/api/users/stats/
```

### Estrutura de Comunicação
```javascript
// Enviar mensagem para background script
chrome.runtime.sendMessage({
  action: 'useShortcut',
  shortcutId: 123,
  variables: { nome: 'João' }
});

// Resposta
{
  content: 'Olá João, bem-vindo ao sistema!',
  success: true
}
```

## 🔄 Atualizações

### Atualizações Automáticas
- **Chrome Web Store**: Atualizações automáticas quando disponíveis
- **Notificações**: Aviso sobre novas funcionalidades
- **Compatibilidade**: Sempre compatível com a versão mais recente do backend

### Versionamento
- **1.0.0**: Versão inicial com funcionalidades básicas
- **1.1.0**: Busca rápida e melhorias de performance
- **1.2.0**: Suporte a templates compartilhados (planejado)

## 🤝 Contribuição

### Como Contribuir
1. Fork este repositório
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

### Desenvolvimento Local
```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
cd symplifika_django/chrome_extension

# 2. Carregue a extensão no Chrome
# Vá para chrome://extensions/
# Ative o modo desenvolvedor
# Clique em "Carregar sem compactação"
# Selecione esta pasta

# 3. Faça suas modificações
# A extensão será recarregada automaticamente
```

### Diretrizes
- **Código limpo**: Siga as convenções de JavaScript
- **Documentação**: Comente funções complexas
- **Testes**: Teste em diferentes sites e cenários
- **Performance**: Mantenha o impacto mínimo na navegação

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](../LICENSE) para detalhes.

## 📞 Suporte

### Canais de Suporte
- **Issues do GitHub**: Para bugs e solicitações de features
- **Email**: suporte@symplifika.com
- **Documentação**: Wiki do projeto

### FAQ

**P: A extensão funciona em todos os sites?**
R: Sim, a extensão funciona em qualquer campo de texto de qualquer site.

**P: Preciso estar sempre online para usar?**
R: Não, os atalhos ficam em cache local. Apenas a expansão com IA requer internet.

**P: Posso usar com múltiplas contas?**
R: Atualmente suportamos apenas uma conta por vez. Logout/login para trocar.

**P: A extensão consome muitos recursos?**
R: Não, a extensão é otimizada para ter impacto mínimo na performance.

**P: Como faço backup dos meus atalhos?**
R: Os atalhos ficam no servidor, mas você pode exportar as configurações.

---

**Desenvolvido com ❤️ pela equipe Symplifika**

Para mais informações, visite [symplifika.com](https://symplifika.com)