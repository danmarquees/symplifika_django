# Templates Django - Symplifika

Este documento descreve a estrutura de templates corrigida e otimizada para seguir as melhores práticas do Django.

## Estrutura dos Templates

### Templates Base

#### `base.html`
Template principal que serve como base para todos os outros templates. Inclui:
- Meta tags para SEO e responsividade
- Sistema de blocos Django para herança
- Integração com arquivos estáticos
- Sistema de mensagens do Django
- CSRF tokens para segurança
- JavaScript base para funcionalidades comuns

#### Blocos Principais:
- `{% block title %}` - Título da página
- `{% block meta_description %}` - Descrição meta
- `{% block html_class %}` - Classes do elemento HTML
- `{% block body_class %}` - Classes do body
- `{% block navigation %}` - Área de navegação
- `{% block content %}` - Conteúdo principal
- `{% block footer %}` - Rodapé
- `{% block extra_css %}` - CSS adicional
- `{% block extra_js %}` - JavaScript adicional

### Templates de Páginas

#### `index.html`
Página inicial do site com:
- Hero section responsiva
- Seção de recursos
- Seção sobre o projeto
- Call-to-action
- Animações e efeitos visuais

#### `app.html`
Dashboard principal da aplicação:
- Layout com sidebar e conteúdo principal
- Sistema de navegação entre páginas
- Interface para gerenciar atalhos
- Área de estatísticas
- Configurações do usuário

### Templates de Autenticação

#### `auth/login.html`
- Formulário de login com validação
- Integração com sistema de autenticação Django
- Toggle de visibilidade de senha
- Credenciais de demonstração
- Redirecionamento após login

#### `auth/register.html`
- Formulário de registro completo
- Validação de senha com indicador de força
- Confirmação de senha
- Termos de uso e política de privacidade
- Validação em tempo real

### Templates de Erro

#### `404.html`
Página de erro 404 com:
- Design consistente com o site
- Sugestões de ação para o usuário
- Links úteis para navegação
- Funcionalidade de busca
- Botão "voltar"

#### `500.html`
Página de erro interno do servidor:
- Informações sobre o status do sistema
- Botões para tentar novamente
- Contato para suporte
- Informações de debug (apenas em desenvolvimento)
- Timestamp do erro

### Componentes Reutilizáveis

#### `includes/navbar.html`
Barra de navegação responsiva com:
- Logo e branding
- Menu de navegação adaptável
- Menu do usuário com dropdown
- Toggle de tema
- Botão de logout
- Versão mobile com menu hambúrguer

#### `includes/footer.html`
Rodapé completo contendo:
- Informações da empresa
- Links de navegação
- Links de suporte
- Redes sociais
- Informações legais
- Botão "voltar ao topo"

## Arquivos Estáticos

### CSS

#### `static/css/base.css`
Estilos base do projeto:
- Variáveis CSS para cores do brand
- Componentes reutilizáveis (cards, botões, forms)
- Sistema de layout responsivo
- Animações e transições
- Modo escuro
- Estilos de impressão
- Acessibilidade

#### `static/css/app.css`
Estilos específicos da aplicação:
- Layout do dashboard
- Sidebar e navegação
- Cards de atalhos e categorias
- Estados de carregamento
- Modais e overlays
- Responsividade mobile

### JavaScript

#### `static/js/base.js`
JavaScript base com:
- Utilitários comuns
- Sistema de notificações (Toast)
- Gerenciamento de modais
- API helper para requisições
- Validação de formulários
- Sistema de temas
- Tratamento de erros globais

#### `static/js/app.js`
JavaScript da aplicação:
- Classe principal SymplifikaApp
- Gerenciamento de estado
- Navegação entre páginas
- CRUD de atalhos e categorias
- Filtros e busca
- Integração com API Django

## Padrões e Convenções

### Django Template Tags
- Uso correto de `{% load static %}`
- `{% csrf_token %}` em todos os formulários
- `{% url %}` para geração de URLs
- `{% block %}` para herança de templates
- Filtros Django para formatação

### Estrutura de Arquivos
```
templates/
├── base.html                 # Template base
├── index.html               # Página inicial
├── app.html                 # Dashboard
├── 404.html                 # Erro 404
├── 500.html                 # Erro 500
├── auth/
│   ├── login.html          # Login
│   └── register.html       # Registro
└── includes/
    ├── navbar.html         # Navegação
    └── footer.html         # Rodapé
```

### Responsividade
- Design mobile-first
- Breakpoints padrão do Tailwind CSS
- Componentes adaptativos
- Touch-friendly em dispositivos móveis

### Acessibilidade
- Texto alternativo em imagens
- Labels apropriados em formulários
- Navegação por teclado
- Contraste adequado
- Semântica HTML correta

### SEO
- Meta tags estruturadas
- Títulos descritivos
- URLs amigáveis
- Schema markup (onde aplicável)
- Sitemap e robots.txt

## Segurança

### CSRF Protection
- Tokens CSRF em todos os formulários
- Verificação automática pelo Django
- Headers para requisições AJAX

### XSS Prevention
- Escape automático de templates Django
- Validação de entrada de dados
- CSP headers (recomendado)

### Autenticação
- Sistema de sessões Django
- Redirecionamento após login/logout
- Proteção de páginas privadas

## Performance

### Otimizações
- Lazy loading de imagens
- Minificação de CSS/JS (produção)
- Compressão de arquivos estáticos
- Cache de templates Django

### Loading States
- Spinners para carregamento
- Estados vazios informativos
- Feedback visual para ações do usuário

## Manutenibilidade

### Componentização
- Templates reutilizáveis
- Includes para componentes comuns
- CSS modular e organizado
- JavaScript em classes

### Documentação
- Comentários em templates complexos
- README para cada seção
- Exemplos de uso
- Convenções de nomenclatura

## Próximos Passos

1. **Testes**: Implementar testes para templates
2. **i18n**: Adicionar internacionalização
3. **PWA**: Implementar Service Workers
4. **Analytics**: Integrar Google Analytics
5. **Monitoring**: Adicionar monitoramento de erros

## Comandos Úteis

### Desenvolvimento
```bash
# Servir arquivos estáticos
python manage.py collectstatic

# Verificar templates
python manage.py check

# Executar servidor de desenvolvimento
python manage.py runserver
```

### Produção
```bash
# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Verificar configuração
python manage.py check --deploy
```

## Contribuição

Ao modificar templates:
1. Seguir as convenções estabelecidas
2. Testar em diferentes dispositivos
3. Verificar acessibilidade
4. Atualizar documentação se necessário
5. Commit com mensagens descritivas