# Sistema de Atualização de Status do Plano

## Visão Geral

Este documento descreve o sistema implementado para atualizar automaticamente o status do plano do usuário no dashboard após um upgrade, sem necessidade de recarregar a página.

## Funcionalidades Implementadas

### 1. Atualização Automática do Status do Plano

O sistema monitora mudanças no status do plano do usuário e atualiza a interface automaticamente quando detecta uma alteração.

#### Elementos da Interface Atualizados:

- **Badge do Plano Principal** (`#userPlanBadge`): Mostra o status atual do plano na sidebar
- **Badge do Plano de IA** (`#aiPlanBadge`): Exibe o plano na seção de prompts IA
- **Label de Uso de IA** (`#aiUsagePlanLabel`): Label do plano na barra de uso de IA
- **Card de Upgrade** (`#upgradeCardContainer`): Oculta/mostra baseado no plano
- **Estatísticas de Uso de IA**: Atualiza limites e contadores

### 2. Endpoints de API

#### `/api/dashboard/stats/` (Aprimorado)
Retorna estatísticas completas do dashboard incluindo informações detalhadas do plano:

```json
{
  "total_shortcuts": 25,
  "active_shortcuts": 20,
  "total_categories": 5,
  "usages_today": 12,
  "total_usages": 150,
  "time_saved": "2.5h",
  "ai_requests_used": 35,
  "ai_requests_remaining": 465,
  "max_ai_requests": 500,
  "max_ai_requests_free": 50,
  "plan": "premium",
  "plan_display": "Premium",
  "max_shortcuts": 500,
  "weekly_usage": [...],
  "user_full_name": "João Silva"
}
```

#### `/api/plan/status/` (Novo)
Endpoint otimizado para verificações rápidas de status do plano:

```json
{
  "plan": "premium",
  "plan_display": "Premium",
  "ai_requests_used": 35,
  "max_ai_requests": 500,
  "max_ai_requests_free": 50,
  "max_shortcuts": 500,
  "last_updated": "2024-01-20T15:30:00Z"
}
```

### 3. Monitoramento e Detecção de Mudanças

#### Verificação Periódica
- **Intervalo**: A cada 30 segundos
- **Endpoint**: `/api/plan/status/` (otimizado para performance)
- **Comparação**: Verifica se o texto do plano mudou na interface

#### Detecção de Retorno do Checkout
- **Focus Event**: Monitora quando a janela ganha foco (usuário voltou do Stripe)
- **URL Parameters**: Detecta parâmetros de sucesso (`checkout=success` ou `session_id`)
- **Delay**: Aguarda 2-3 segundos para o webhook processar

### 4. Atualização da Interface

#### Métodos JavaScript Implementados:

```javascript
// Atualiza todos os elementos relacionados ao plano
updatePlanStatus(stats)

// Atualiza o badge principal do plano
updatePlanBadge(plan, planDisplay)

// Atualiza o badge do plano na seção de IA
updateAIPlanBadge(plan, planDisplay)

// Atualiza o label do plano na barra de uso
updateAIUsagePlanLabel(plan, planDisplay)

// Mostra/oculta o card de upgrade
toggleUpgradeCard(plan)

// Força uma verificação manual
refreshPlanStatus()
```

#### Classes CSS Dinâmicas:

**Plano Free:**
```css
.bg-gray-100.text-gray-800.dark:bg-gray-700.dark:text-gray-300
```

**Plano Premium:**
```css
.bg-symplifika-primary/20.text-symplifika-primary
```

**Plano Enterprise:**
```css
.bg-purple-100.text-purple-800.dark:bg-purple-900.dark:text-purple-300
```

### 5. Notificações de Upgrade

#### Toast Notification
- Mensagem personalizada com emoji baseado no plano
- Duração estendida (5 segundos)
- Cores e estilos específicos por plano

#### Browser Notification (Opcional)
- Notificação nativa do navegador se permissão concedida
- Título: "Symplifika - Plano Atualizado"
- Ícone personalizado da aplicação

### 6. Integração com Sistema de Pagamentos

#### Stripe Webhooks
O sistema continua funcionando com os webhooks existentes:

- `checkout.session.completed`: Atualiza plano após pagamento
- `customer.subscription.updated`: Sincroniza mudanças de assinatura
- `customer.subscription.deleted`: Reverte para plano gratuito

#### StripeService
Métodos que atualizam o UserProfile:
- `handle_checkout_session_completed()`
- `_handle_subscription_updated()`
- `_handle_subscription_deleted()`

## Fluxo de Atualização

### Após Upgrade bem-sucedido:

1. **Webhook Stripe** → Atualiza `UserProfile.plan` no banco
2. **Verificação Periódica** → Detecta mudança via `/api/plan/status/`
3. **Atualização Interface** → Chama `updatePlanStatus()` com novos dados
4. **Notificação** → Mostra toast e notificação do browser
5. **Reload Completo** → Carrega `/api/dashboard/stats/` para dados completos
6. **Modal Cleanup** → Fecha modal de upgrade se aberto

### Detecção de Mudanças:

```javascript
// Comparação de texto do plano atual vs novo
const planTextMap = {
  free: "gratuito",
  premium: "premium", 
  enterprise: "enterprise"
};

if (planTextMap[newPlan] !== currentPlanText) {
  // Plano mudou - atualizar interface
}
```

## Configuração e Inicialização

### No `app.js`:

```javascript
init() {
  // ... outras inicializações
  this.setupPeriodicPlanCheck();
  this.setupCheckoutReturnListener();
}
```

### Template HTML:
- Adicionados IDs únicos para todos os elementos do plano
- Container do card de upgrade com classe condicional
- Estrutura preparada para atualizações dinâmicas

## Performance e Otimizações

### Endpoint Otimizado
- `/api/plan/status/` retorna apenas dados essenciais
- Reduz tráfego de rede em verificações periódicas
- Cache-friendly com timestamp de última atualização

### Prevenção de Memory Leaks
- Método `stopPeriodicPlanCheck()` para cleanup
- Listeners de eventos removíveis
- Timers controlados adequadamente

### Throttling
- Verificações limitadas a 30 segundos
- Delay adicional em eventos de foco
- Evita requests desnecessários

## Tratamento de Erros

- Try/catch em todas as requisições AJAX
- Fallbacks silenciosos para elementos não encontrados
- Logs detalhados para debugging
- Graceful degradation se APIs não respondem

## Compatibilidade

- Funciona com todos os planos existentes (Free, Premium, Enterprise)
- Compatível com sistema de webhooks atual
- Não quebra funcionalidade existente
- Progressive enhancement - funciona mesmo se JavaScript falhar

## Monitoramento

### Logs Disponíveis:
- "Erro ao verificar mudança do plano"
- "Plano atualizado para X!"
- "Erro ao atualizar status do plano"

### Métricas Sugeridas:
- Frequência de verificações de plano
- Taxa de detecção de upgrades
- Tempo entre upgrade e detecção na interface