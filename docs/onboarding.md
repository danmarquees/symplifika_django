symplifika_django/docs/onboarding.md
```

# Onboarding para Novos Desenvolvedores

Bem-vindo ao Symplifika! Este guia tem como objetivo acelerar seu processo de ambientação no projeto, apresentando os principais passos para rodar o sistema localmente, entender a arquitetura, contribuir com código e seguir as melhores práticas do time.

---

## 1. Visão Geral do Projeto

O Symplifika é uma plataforma para criação e gerenciamento de atalhos de texto inteligentes, integrando web, API RESTful, IA (Google Gemini), pagamentos (Stripe) e uma extensão Chrome. O backend é desenvolvido em Django, com frontend responsivo e integração contínua via GitHub Actions.

---

## 2. Pré-requisitos

- Python 3.11+
- Git
- Node.js (opcional, para build de assets estáticos ou extensão Chrome)
- Conta no Render (opcional, para deploy)
- Editor recomendado: VSCode ou PyCharm

---

## 3. Clonando o Repositório

```bash
git clone https://github.com/seuusuario/symplifika.git
cd symplifika_django
```

---

## 4. Configurando o Ambiente

### Ambiente Virtual

```bash
python -m venv venv
source venv/bin/activate
```

### Instalando Dependências

```bash
pip install -r requirements.txt
```

### Variáveis de Ambiente

- Copie o arquivo de exemplo:
  ```bash
  cp env_example.txt .env
  ```
- Edite o `.env` com suas chaves e configurações locais.

Principais variáveis:
- `SECRET_KEY`
- `DEBUG`
- `DATABASE_URL`
- `GEMINI_API_KEY`
- `STRIPE_PUBLISHABLE_KEY`
- `STRIPE_SECRET_KEY`

---

## 5. Inicializando o Banco de Dados

```bash
python manage.py migrate
```

Se desejar criar um superusuário para acessar o admin:

```bash
python manage.py createsuperuser
```

---

## 6. Rodando o Servidor Local

```bash
python manage.py runserver
```

Acesse em [http://localhost:8000](http://localhost:8000)

---

## 7. Rodando os Testes

```bash
python manage.py test
```

---

## 8. Estrutura dos Diretórios

- `core/` — Lógica principal, views, templates centrais
- `users/` — Autenticação, perfis, assinaturas
- `payments/` — Integração com Stripe
- `chrome_extension/` — Código da extensão Chrome
- `templates/` — Templates HTML
- `static/` — Arquivos estáticos (CSS, JS, imagens)
- `docs/` — Documentação técnica, exemplos, diagramas

---

## 9. Fluxo de Desenvolvimento

1. Crie uma branch a partir de `main`:
   ```bash
   git checkout -b feature/nome-da-sua-feature
   ```
2. Faça commits pequenos e descritivos.
3. Antes de abrir um PR, rode os testes e o lint:
   ```bash
   python manage.py test
   flake8 .
   ```
4. Abra um Pull Request detalhando o que foi feito.

---

## 10. Boas Práticas

- Siga o padrão PEP8 para Python.
- Use nomes claros para funções, variáveis e commits.
- Prefira funções pequenas e reutilizáveis.
- Documente endpoints e funções complexas.
- Sempre proteja endpoints sensíveis com autenticação.
- Utilize variáveis de ambiente para segredos e chaves.

---

## 11. Recursos Úteis

- [Exemplos de integração](./examples.md)
- [Diagrama de arquitetura](./architecture.md)
- [Guia de deploy no Render](./deploy.md)
- [Documentação Swagger/OpenAPI](http://localhost:8000/api/docs/)

---

## 12. Suporte

Em caso de dúvidas, abra uma issue no GitHub ou entre em contato com o mantenedor do projeto.

---

Seja bem-vindo ao Symplifika e boas contribuições!