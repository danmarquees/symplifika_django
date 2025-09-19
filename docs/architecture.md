# Arquitetura do Sistema Symplifika

Abaixo está um diagrama de alto nível da arquitetura do Symplifika, incluindo os principais fluxos entre usuários, frontend (web e extensão Chrome), backend Django e serviços externos.

```mermaid
flowchart TD
    subgraph Usuário
        U1[Usuário Web]
        U2[Usuário Extensão Chrome]
    end

    subgraph Frontend
        FW[Web (Django Templates)]
        FC[Extensão Chrome]
    end

    subgraph Backend
        DJ[Django Backend + API REST]
    end

    subgraph Serviços_Externos
        ST[Stripe (Pagamentos)]
        GM[Google Gemini (IA)]
        SN[Sentry (Monitoramento)]
        SL[Slack (Alertas)]
        DB[(Banco de Dados)]
    end

    U1 --> FW
    U2 --> FC

    FW <--> DJ
    FC <--> DJ

    DJ <--> DB
    DJ --> ST
    DJ --> GM
    DJ --> SN
    DJ --> SL

    classDef ext fill:#f9f,stroke:#333,stroke-width:1px;
    class Serviços_Externos ext;
```

---

## Descrição dos Componentes

- **Usuário Web**: Interage via navegador com o painel web responsivo.
- **Usuário Extensão Chrome**: Usa atalhos e recursos diretamente no navegador via extensão.
- **Web (Django Templates)**: Interface web tradicional, renderizada pelo Django.
- **Extensão Chrome**: Cliente leve que consome a API do backend para sincronizar atalhos e autenticação.
- **Django Backend + API REST**: Núcleo do sistema, gerencia autenticação, lógica de negócios, endpoints REST, integração com IA e pagamentos.
- **Banco de Dados**: Armazena usuários, atalhos, planos, histórico, etc.
- **Stripe**: Processamento de pagamentos e gestão de assinaturas.
- **Google Gemini**: Serviços de IA para expansão de textos e atalhos inteligentes.
- **Sentry**: Monitoramento de erros e exceções em produção.
- **Slack**: Recebe alertas críticos e notificações administrativas.

---

## Fluxos Principais

- Usuários acessam o sistema via web ou extensão Chrome.
- Frontend consome a API REST do backend Django para autenticação, atalhos, IA, etc.
- Backend integra com Stripe para pagamentos, Gemini para IA, Sentry para monitoramento e Slack para alertas.
- Todas as operações críticas são persistidas no banco de dados.

---

> Para detalhes de endpoints e exemplos de integração, veja `docs/examples.md`.