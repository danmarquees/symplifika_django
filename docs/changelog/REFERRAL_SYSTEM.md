# Sistema de Indicação - Symplifika

## Visão Geral

Este documento descreve a implementação completa do sistema de indicação (referral system) no Symplifika Django. O sistema permite que usuários indiquem outros usuários e ganhem recompensas quando seus indicados fazem upgrade de plano.

## Funcionalidades Implementadas

### 1. Modelo de Dados

**Campos adicionados ao UserProfile:**
- `referred_by`: ForeignKey para o usuário que fez a indicação
- `referral_code`: Código único de indicação (gerado automaticamente)
- `total_referrals`: Contador total de usuários indicados
- `referral_plan_upgrades`: Contador de indicados que fizeram upgrade
- `referral_bonus_earned`: Valor total ganho em bônus por indicações

### 2. Sistema de Bônus

**Valores de Bônus:**
- Premium: R$ 10,00 por upgrade
- Enterprise: R$ 25,00 por upgrade
- Gratuito: R$ 0,00

**Condições para Bônus:**
- O usuário deve ter sido indicado por outro usuário
- O usuário deve sair do plano gratuito (fazer upgrade)
- O bônus é processado automaticamente quando o upgrade é confirmado

### 3. Geração de Códigos de Indicação

**Formato:** `{3 PRIMEIROS CHARS DO USERNAME}{USER_ID}{4 CHARS ALEATÓRIOS}`
- Exemplo: `JOH1234ABCD` (para usuário "john" com ID 123)
- Códigos são únicos e gerados automaticamente na criação do perfil
- Algoritmo evita colisões verificando códigos existentes

### 4. APIs Implementadas

**Endpoints de Indicação:**
```
POST /users/api/referral/create/ - Criar indicação usando código
GET  /users/api/referral/dashboard/ - Dashboard de indicações do usuário
GET  /users/api/referral/generate-code/ - Gerar/obter código de indicação
GET  /users/api/referral/leaderboard/ - Ranking de indicadores
POST /users/api/auth/register-with-referral/ - Registro com indicação
```

**Endpoints de Usuário Atualizados:**
- Registro suporta parâmetro `referral_code`
- Templates de registro incluem campo opcional de código

### 5. Integração com Sistema de Pagamentos

**Hooks de Processamento:**
- `StripeService.handle_checkout_session_completed()` - Processa bônus no checkout
- `StripeService._handle_payment_succeeded()` - Processa bônus em pagamentos
- `StripeService.create_subscription()` - Processa bônus na criação de assinatura
- `PlanUpgradeRequest.approve()` - Processa bônus na aprovação manual

### 6. Interface de Administração

**Funcionalidades Admin:**
- Visualização de estatísticas de indicação na lista de usuários
- Ações em massa para gerar códigos e resetar estatísticas
- Fieldsets organizados para campos de indicação
- Filtros por usuários indicadores

**Ações Disponíveis:**
- `generate_referral_codes` - Gera códigos para usuários sem código
- `reset_referral_stats` - Reseta estatísticas de indicação

### 7. Template Web

**Página de Indicação (`/users/referral/`):**
- Dashboard com estatísticas pessoais
- Lista de usuários indicados
- Botões de compartilhamento (WhatsApp, Telegram, Email)
- Ranking top 5 indicadores
- Como funciona o sistema

**Página de Registro:**
- Campo opcional para código de indicação
- Suporte a URL com parâmetro `?ref=CODIGO`
- Feedback visual para códigos válidos/inválidos

## Arquivos Modificados/Criados

### Modelos
- `users/models.py` - Campos de indicação adicionados ao UserProfile
- `users/migrations/` - Migrations para adicionar campos e popular dados

### Serviços
- `users/services.py` - `ReferralService` para lógica de indicação
- `payments/services.py` - Hooks de bônus em upgrades de plano

### Views
- `users/views.py` - APIs e templates views para indicação
- `users/urls.py` - URLs para endpoints de indicação

### Templates
- `templates/users/referral.html` - Interface web do sistema
- `templates/auth/register.html` - Campo de indicação no registro

### Administração
- `users/admin.py` - Interface admin com campos e ações de indicação

### Comandos de Gerenciamento
- `users/management/commands/process_referral_bonuses.py` - Processamento de bônus

## Como Usar

### 1. Para Usuários

**Obter Código de Indicação:**
```javascript
GET /users/api/referral/generate-code/
```

**Visualizar Dashboard:**
```javascript
GET /users/api/referral/dashboard/
```

**Registrar com Indicação:**
```javascript
POST /users/api/auth/register-with-referral/
{
    "username": "novousuario",
    "email": "novo@email.com",
    "password": "senha123",
    "referral_code": "ABC123DEFG"
}
```

### 2. Para Desenvolvedores

**Processar Bônus Manualmente:**
```bash
python manage.py process_referral_bonuses --dry-run
python manage.py process_referral_bonuses --user-id 123
```

**Gerar Códigos em Massa:**
```python
from users.models import UserProfile
profiles = UserProfile.objects.filter(referral_code__isnull=True)
for profile in profiles:
    profile.generate_referral_code()
```

### 3. Para Administradores

**Via Django Admin:**
1. Acesse `/admin/users/userprofile/`
2. Use ações em massa para gerenciar códigos
3. Visualize estatísticas na lista de usuários

## Fluxo de Funcionamento

### 1. Registro com Indicação
```
1. Usuário A compartilha código: ABC123DEFG
2. Usuário B acessa: /register?ref=ABC123DEFG
3. Usuário B se registra (código preenchido automaticamente)
4. Sistema cria relação: B.referred_by = A
5. A.total_referrals += 1
```

### 2. Processamento de Bônus
```
1. Usuário B faz upgrade para Premium
2. Webhook/Service detecta mudança de plano
3. Sistema verifica: B.referred_by existe?
4. Sistema calcula: bônus = R$ 10 (Premium)
5. A.referral_bonus_earned += 10
6. A.referral_plan_upgrades += 1
7. Notificação enviada para A (se sistema existir)
```

## Configurações

### Valores de Bônus
```python
# Em users/services.py - ReferralService.calculate_referral_bonus()
BONUS_MAPPING = {
    'premium': 10.00,      # R$ 10
    'enterprise': 25.00,   # R$ 25
    'free': 0.00
}
```

### URLs de Indicação
```python
# Formato do link gerado
f"{SITE_URL}/register?ref={referral_code}"
```

## Monitoramento e Relatórios

### Métricas Disponíveis
- Total de usuários indicadores
- Taxa de conversão global (upgrades/indicações)
- Valor total distribuído em bônus
- Ranking de top indicadores

### Logs
- Processamento de bônus é logado
- Erros de indicação são registrados
- Webhooks de pagamento incluem logs de bônus

## Testes e Validação

### Cenários Testados
1. ✅ Registro com código válido
2. ✅ Registro com código inválido
3. ✅ Registro sem código (opcional)
4. ✅ Upgrade de plano com bônus
5. ✅ Geração automática de códigos únicos
6. ✅ Prevenção de auto-indicação
7. ✅ Prevenção de indicação dupla

### Command de Teste
```bash
# Teste sem alterações
python manage.py process_referral_bonuses --dry-run

# Processamento real
python manage.py process_referral_bonuses

# Usuário específico
python manage.py process_referral_bonuses --user-id 123
```

## Próximos Passos Sugeridos

1. **Sistema de Notificações**: Avisar indicadores sobre bônus ganhos
2. **Pagamento de Bônus**: Integrar com gateway para pagamentos reais
3. **Gamificação**: Badges, níveis, recompensas especiais
4. **Analytics**: Dashboard detalhado com gráficos e métricas
5. **API Mobile**: Endpoints otimizados para aplicativo móvel
6. **Testes Automatizados**: Suite completa de testes unitários
7. **Relatórios Financeiros**: Exportação de dados para contabilidade

## Troubleshooting

### Problemas Comuns

**Erro de código duplicado:**
```bash
python manage.py shell
>>> from users.models import UserProfile
>>> UserProfile.objects.filter(referral_code__isnull=True).update(referral_code=None)
>>> # Execute migration novamente
```

**Bônus não processado:**
```bash
python manage.py process_referral_bonuses --user-id <USER_ID>
```

**Códigos não únicos:**
```python
# Verificar códigos duplicados
from users.models import UserProfile
from django.db.models import Count
duplicates = UserProfile.objects.values('referral_code').annotate(
    count=Count('referral_code')
).filter(count__gt=1)
```

## Segurança

### Validações Implementadas
- Códigos únicos obrigatórios
- Prevenção de auto-indicação
- Validação de usuário existente
- Limite de tentativas de geração de código (anti-loop)

### Considerações
- Logs de todas as operações de bônus
- Validação de integridade nos webhooks
- Sanitização de inputs de código

---

**Versão:** 1.0  
**Data:** Dezembro 2024  
**Autor:** Sistema Symplifika  
**Status:** ✅ Implementado e Funcionando