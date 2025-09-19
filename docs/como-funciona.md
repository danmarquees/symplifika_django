# O que é o Symplifika?

O **Symplifika** é uma plataforma de produtividade que automatiza e gerencia atalhos de texto inteligentes para uso pessoal ou profissional. Ela permite que usuários criem, organizem e utilizem atalhos de texto tanto em um painel web responsivo quanto diretamente no navegador através de uma extensão Chrome. A plataforma integra recursos avançados como Inteligência Artificial (Google Gemini) para expansão e sugestão de textos, autenticação segura, API RESTful para integrações externas, e pagamentos recorrentes via Stripe para planos premium.

**O que o Symplifika faz?**
- Permite criar atalhos de texto personalizados e inteligentes.
- Sincroniza atalhos entre o painel web e a extensão Chrome.
- Oferece sugestões e expansão de textos usando IA.
- Gera estatísticas de uso, histórico e economia de tempo.
- Gerencia assinaturas e pagamentos para recursos avançados.
- Expõe uma API RESTful para integrações externas e automações.

**Como funciona?**
1. O usuário se cadastra e faz login via web ou extensão.
2. Cria e organiza atalhos de texto, podendo usar variáveis dinâmicas e IA.
3. Usa os atalhos no navegador (via extensão) ou no painel web.
4. Todos os atalhos e configurações são sincronizados automaticamente.
5. Recursos premium podem ser ativados via assinatura paga.
6. Toda a comunicação é protegida por autenticação JWT, monitoramento de erros e boas práticas de segurança.

---

# Como Funciona a Plataforma Symplifika

## Sumário

1. [Visão Geral](#visão-geral)
2. [Principais Componentes](#principais-componentes)
3. [Fluxo do Usuário](#fluxo-do-usuário)
4. [Atalhos Inteligentes](#atalhos-inteligentes)
5. [API REST e Integração](#api-rest-e-integração)
6. [Extensão Chrome](#extensão-chrome)
7. [Integração com IA (Google Gemini)](#integração-com-ia-google-gemini)
8. [Gestão de Usuários e Assinaturas](#gestão-de-usuários-e-assinaturas)
9. [Pagamentos e Planos](#pagamentos-e-planos)
10. [Segurança e Monitoramento](#segurança-e-monitoramento)
11. [Fluxo de Deploy e CI/CD](#fluxo-de-deploy-e-cicd)
12. [Arquitetura Resumida](#arquitetura-resumida)
13. [Referências e Recursos](#referências-e-recursos)

---

## Visão Geral

O **Symplifika** é uma plataforma de produtividade que permite criar, gerenciar e utilizar atalhos de texto inteligentes, tanto via painel web quanto por uma extensão Chrome. A plataforma integra recursos de Inteligência Artificial (IA), autenticação segura, API RESTful, pagamentos recorrentes e monitoramento, visando facilitar o dia a dia de profissionais e equipes.

---

## Principais Componentes

- **Frontend Web:** Interface responsiva para gerenciamento de atalhos, configurações, perfil e assinatura.
- **Extensão Chrome:** Permite usar e sincronizar atalhos diretamente no navegador.
- **Backend Django:** API RESTful, lógica de negócios, autenticação, integração com IA e pagamentos.
- **Banco de Dados:** Armazena usuários, atalhos, histórico, planos, etc.
- **Serviços Externos:** Stripe (pagamentos), Google Gemini (IA), Sentry (monitoramento), Slack (alertas).

---

## Fluxo do Usuário

1. **Cadastro e Login:** O usuário cria uma conta ou faz login via painel web ou extensão.
2. **Criação de Atalhos:** O usuário cadastra atalhos personalizados, podendo categorizá-los e definir conteúdos dinâmicos.
3. **Uso dos Atalhos:** Os atalhos podem ser utilizados no painel web ou diretamente em qualquer campo de texto do navegador via extensão Chrome.
4. **Sincronização:** Atalhos e configurações são sincronizados automaticamente entre web e extensão.
5. **Funcionalidades Avançadas:** Usuários podem expandir textos com IA, visualizar estatísticas de uso, gerenciar assinatura e acessar histórico.
6. **Pagamentos:** Para recursos premium, o usuário pode assinar planos pagos via Stripe.
7. **Notificações e Monitoramento:** Atividades críticas são monitoradas e notificadas via Sentry e Slack.

---

## Atalhos Inteligentes

- **Criação:** O usuário define um título, conteúdo e categoria para cada atalho.
- **Personalização:** Atalhos podem conter variáveis dinâmicas (ex: nome do cliente, data atual).
- **Sugestões de IA:** A plataforma pode sugerir ou expandir textos usando IA (Google Gemini).
- **Organização:** Atalhos podem ser organizados por categorias e marcados como favoritos.
- **Estatísticas:** O painel mostra uso, atalhos mais acessados e tempo economizado.

---

## API REST e Integração

- **Endpoints RESTful:** Toda a lógica de atalhos, usuários, assinaturas e IA é exposta via API protegida por JWT.
- **Autenticação:** Login e refresh de tokens via endpoints dedicados.
- **Documentação Interativa:** Disponível via Swagger/OpenAPI em `/api/docs/`.
- **Integração Externa:** Permite que outros sistemas ou automações consumam a API para criar/usar atalhos, consultar perfil, etc.

---

## Extensão Chrome

- **Instalação:** O usuário instala a extensão em modo desenvolvedor ou via Chrome Web Store.
- **Login:** Autenticação via painel da extensão, usando as mesmas credenciais do painel web.
- **Sincronização:** Atalhos são sincronizados automaticamente com o backend.
- **Uso Rápido:** O usuário pode inserir atalhos em qualquer campo de texto do navegador com poucos cliques ou atalhos de teclado.
- **Criação e Edição:** Também é possível criar e editar atalhos diretamente pela extensão.

---

## Integração com IA (Google Gemini)

- **Expansão de Texto:** Usuários podem enviar prompts para a IA expandir, resumir ou melhorar textos.
- **Sugestões Inteligentes:** A IA pode sugerir novos atalhos ou respostas automáticas.
- **Configuração:** A chave da API Gemini é configurada via variável de ambiente.
- **Endpoints Dedicados:** A API possui endpoints específicos para interação com a IA.

---

## Gestão de Usuários e Assinaturas

- **Cadastro e Login:** Via painel web ou extensão, com autenticação JWT.
- **Perfil:** Cada usuário possui perfil com avatar, bio, estatísticas e preferências.
- **Assinatura:** Usuários podem visualizar e gerenciar seu plano (gratuito ou pago).
- **Permissões:** Recursos premium são liberados conforme o plano ativo.

---

## Pagamentos e Planos

- **Stripe:** Integração completa para cobrança recorrente, upgrades, downgrades e cancelamentos.
- **Histórico:** O usuário pode consultar faturas e histórico de pagamentos.
- **Planos:** Diferentes planos com limites de uso, acesso à IA, etc.

---

## Segurança e Monitoramento

- **Autenticação JWT:** Protege todas as rotas sensíveis da API.
- **Rate Limiting:** Limita tentativas de login e protege contra brute force.
- **Proteção CSRF:** Em todos os formulários web.
- **Monitoramento:** Erros são enviados automaticamente para o Sentry.
- **Alertas:** Atividades suspeitas e falhas críticas são notificadas via Slack.
- **Privacidade:** Dados sensíveis protegidos e conformidade com LGPD/GDPR.

---

## Fluxo de Deploy e CI/CD

- **GitHub Actions:** Pipeline automatizado para lint, testes, análise de segurança, build de estáticos e deploy.
- **Deploy Automático:** Deploy contínuo para Render (ou outro provedor), disparado após aprovação dos testes.
- **Secrets:** Variáveis sensíveis são gerenciadas via GitHub Secrets e Render Dashboard.
- **Rollback:** Possibilidade de restaurar builds anteriores via painel do Render.

---

## Arquitetura Resumida

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

## Referências e Recursos

- [Exemplos de integração](./examples.md)
- [Diagrama de arquitetura](./architecture.md)
- [Guia de deploy no Render](./deploy.md)
- [Onboarding para desenvolvedores](./onboarding.md)
- [Documentação Swagger/OpenAPI](http://localhost:8000/api/docs/)
- [Documentação da extensão Chrome](../chrome_extension/README.md)
- [Site oficial do Render](https://render.com/)
- [Google Gemini API](https://ai.google.dev/)
- [Stripe](https://stripe.com/)
- [Django](https://www.djangoproject.com/)

---

Em caso de dúvidas, consulte o README do projeto, a documentação técnica ou abra uma issue no repositório.