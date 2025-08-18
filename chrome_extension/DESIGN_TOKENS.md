# Design Tokens - Symplifika Chrome Extension

Este documento define todos os tokens de design utilizados na extensão Chrome, garantindo consistência visual com o projeto principal Django.

## 🎨 Sistema de Cores

### Paleta Principal
```css
:root {
    /* Cores da Marca Symplifika */
    --symplifika-primary: #00c853;    /* Verde Principal */
    --symplifika-secondary: #00ff57;  /* Verde Neon */
    --symplifika-accent: #4caf50;     /* Verde Auxiliar */
    --symplifika-dark: #1a1a1a;      /* Cinza Escuro */
    --symplifika-light: #f8f9fa;     /* Cinza Claro */
}
```

### Escala de Cinzas
```css
/* Tema Claro */
--gray-50: #f9fafb;
--gray-100: #f3f4f6;
--gray-200: #e5e7eb;
--gray-300: #d1d5db;
--gray-400: #9ca3af;
--gray-500: #6b7280;
--gray-600: #4b5563;
--gray-700: #374151;
--gray-800: #1f2937;
--gray-900: #111827;

/* Tema Escuro (Invertido automaticamente) */
--gray-50: #111827;
--gray-100: #1f2937;
--gray-200: #374151;
--gray-300: #4b5563;
--gray-400: #6b7280;
--gray-500: #9ca3af;
--gray-600: #d1d5db;
--gray-700: #e5e7eb;
--gray-800: #f3f4f6;
--gray-900: #ffffff;
```

## 📏 Espaçamento

### Grid de Espaçamento
- **4px** - Micro espaçamento (gaps pequenos)
- **8px** - Espaçamento básico (padding interno)
- **12px** - Espaçamento médio (gaps entre elementos)
- **16px** - Espaçamento padrão (margens)
- **20px** - Espaçamento grande (seções)
- **24px** - Espaçamento extra (containers)
- **32px** - Espaçamento maior (seções principais)
- **40px** - Espaçamento muito grande (separadores)

### Dimensões Específicas
```css
/* Dimensões do Popup */
width: 400px;
min-height: 600px;
max-height: 700px;

/* Dimensões de Elementos */
--avatar-size: 32px;
--icon-size: 16px;
--button-height: 40px;
--input-height: 44px;
```

## 🔤 Tipografia

### Família de Fonte
```css
font-family: "Poppins", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
```

### Escala Tipográfica
```css
/* Tamanhos de Fonte */
--text-xs: 12px;    /* Texto auxiliar */
--text-sm: 13px;    /* Texto pequeno */
--text-base: 14px;  /* Texto padrão */
--text-lg: 16px;    /* Texto grande */
--text-xl: 18px;    /* Títulos pequenos */
--text-2xl: 20px;   /* Títulos médios */
--text-3xl: 24px;   /* Títulos grandes */
--text-4xl: 28px;   /* Títulos principais */

/* Pesos de Fonte */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
--font-extrabold: 800;
```

### Aplicação Tipográfica
```css
/* Headers */
h1 { font-size: var(--text-4xl); font-weight: var(--font-bold); }
h2 { font-size: var(--text-2xl); font-weight: var(--font-semibold); }
h3 { font-size: var(--text-xl); font-weight: var(--font-semibold); }

/* Body Text */
body { font-size: var(--text-base); font-weight: var(--font-normal); }
small, .help-text { font-size: var(--text-xs); }
```

## 🎯 Raios de Borda

```css
--border-radius: 0.5rem;      /* 8px - Padrão */
--border-radius-lg: 0.75rem;  /* 12px - Grande */
--border-radius-xl: 1rem;     /* 16px - Extra grande */
--border-radius-full: 50%;    /* Circular */
```

## 🌊 Sombras

```css
--shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
--shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
--shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
--shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
```

## ⚡ Transições

```css
--transition: all 0.2s ease-in-out;
--transition-fast: all 0.15s ease-in-out;
--transition-slow: all 0.3s ease-in-out;
```

## 🎨 Componentes Específicos

### Botões
```css
.btn {
    padding: 10px 16px;
    border-radius: var(--border-radius);
    font-size: var(--text-base);
    font-weight: var(--font-semibold);
    transition: var(--transition);
}

.btn-primary {
    background: var(--symplifika-primary);
    color: white;
}

.btn-secondary {
    background: var(--gray-100);
    color: var(--gray-700);
}
```

### Cards
```css
.card {
    background: white;
    border-radius: var(--border-radius-lg);
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--gray-200);
}
```

### Inputs
```css
.form-input {
    padding: 12px 16px;
    border: 1px solid var(--gray-300);
    border-radius: var(--border-radius);
    font-size: var(--text-base);
    transition: var(--transition);
}

.form-input:focus {
    border-color: var(--symplifika-primary);
    box-shadow: 0 0 0 3px rgba(0, 200, 83, 0.1);
}
```

## 🎨 Estados Visuais

### Hover Effects
```css
/* Transformação sutil */
transform: translateY(-1px);
box-shadow: var(--shadow-md);

/* Mudança de cor */
background: var(--symplifika-accent);
```

### Focus States
```css
outline: 2px solid var(--symplifika-primary);
outline-offset: 2px;
```

### Disabled States
```css
background: var(--gray-300);
color: var(--gray-500);
cursor: not-allowed;
```

## 🌙 Suporte a Tema Escuro

### Detecção Automática
```css
@media (prefers-color-scheme: dark) {
    /* Inversão automática das variáveis de cinza */
}
```

### Estados Específicos
```css
/* Backgrounds em tema escuro */
background: var(--gray-100); /* Automaticamente escuro */
color: var(--gray-900);      /* Automaticamente claro */
```

## ♿ Acessibilidade

### Contraste Mínimo
- **Texto normal**: 4.5:1
- **Texto grande**: 3:1
- **Interface**: 3:1

### Alto Contraste
```css
@media (prefers-contrast: high) {
    .shortcut-item { border-width: 2px; }
    .btn { border: 2px solid; }
}
```

### Movimento Reduzido
```css
@media (prefers-reduced-motion: reduce) {
    .spinner, .btn, .shortcut-item {
        animation: none;
        transition: none;
    }
}
```

## 📐 Layout Responsivo

### Breakpoints
```css
/* Mobile First Approach */
@media (max-width: 480px) { /* Mobile */ }
@media (max-width: 768px) { /* Tablet */ }
@media (max-width: 1024px) { /* Desktop */ }
```

### Grid System
```css
.settings-grid {
    display: grid;
    gap: 24px;
    
    /* Responsivo automático */
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
}
```

## 🎯 Animações

### Keyframes Principais
```css
@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

@keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}
```

### Performance
- **Preferência**: `transform` e `opacity`
- **Evitar**: `width`, `height`, `top`, `left`
- **GPU Acceleration**: `will-change: transform`

## 📦 Utilitários

### Classes de Utilidade
```css
.hidden { display: none !important; }
.sr-only { /* Screen reader only */ }
.text-center { text-align: center; }
.flex { display: flex; }
.grid { display: grid; }
.relative { position: relative; }
.absolute { position: absolute; }
```

### Estados de Componente
```css
.loading { opacity: 0.6; pointer-events: none; }
.disabled { opacity: 0.5; cursor: not-allowed; }
.active { color: var(--symplifika-primary); }
.error { border-color: #dc2626; }
.success { border-color: var(--symplifika-primary); }
```

## 🔍 Z-Index Scale

```css
--z-dropdown: 1000;
--z-sticky: 1010;
--z-fixed: 1020;
--z-modal-backdrop: 1030;
--z-modal: 1040;
--z-popover: 1050;
--z-tooltip: 1060;
--z-toast: 1070;
```

## 📝 Aplicação Prática

### Exemplo de Componente
```css
.shortcut-item {
    /* Layout */
    padding: 16px;
    border-radius: var(--border-radius-lg);
    
    /* Visual */
    background: white;
    border: 1px solid var(--gray-200);
    box-shadow: var(--shadow-sm);
    
    /* Typography */
    font-size: var(--text-base);
    font-weight: var(--font-normal);
    color: var(--gray-900);
    
    /* Interaction */
    cursor: pointer;
    transition: var(--transition);
}

.shortcut-item:hover {
    border-color: var(--symplifika-primary);
    box-shadow: var(--shadow-md);
    transform: translateY(-1px);
}

/* Tema escuro automático */
@media (prefers-color-scheme: dark) {
    .shortcut-item {
        background: var(--gray-100); /* Automaticamente #1f2937 */
        color: var(--gray-900);      /* Automaticamente #ffffff */
    }
}
```

## ✅ Checklist de Implementação

- [x] Variáveis CSS definidas
- [x] Tipografia Poppins implementada
- [x] Cores da marca aplicadas
- [x] Sombras e bordas padronizadas
- [x] Transições suaves
- [x] Tema escuro automático
- [x] Responsividade mobile-first
- [x] Estados de acessibilidade
- [x] Performance otimizada
- [x] Componentes consistentes

---

**Mantido por**: Equipe de Design Symplifika  
**Última atualização**: Janeiro 2024  
**Versão**: 1.1.0