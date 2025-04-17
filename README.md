# 📘 Matera Loan & Payment API

Este projeto é uma API robusta construída com Django 5.2 e Django REST Framework para o gerenciamento de empréstimos e pagamentos. A ideia é oferecer uma solução simples, segura e performática para aplicações financeiras que lidam com dados sensíveis e transações monetárias.

---

## 🚀 Funcionalidades

- Autenticação com JWT (`rest_framework_simplejwt`)
- CRUD de empréstimos (loans)
- CRUD de pagamentos (payments)
- Sistema de logs de ações em auditoria (audits)
- Validações completas para pagamentos (limite, permissão, duplicidade)
- Pagamentos são transacionais com `transaction.atomic()`
- Throttling para evitar abusos na API
- Filtros com `django-filters`
- Documentação com `drf-spectacular`
- Integração com `coverage` para acompanhar a cobertura dos testes de forma precisa
- CI com GitHub Actions (lint, format, test)

---

## 🥪 Testes

A API conta com uma **base sólida de testes**, cobrindo os principais fluxos de negócio:

- Cobertura de código de aproximadamente 99% _(não garante uma aplicação sem bugs, mas é uma boa métrica)_
- **Mais de 50 testes automatizados** já criados
- Cobertura de criação, edição, validação e quitação de empréstimos

---

## 🐳 Ambiente com Docker

Este projeto usa Docker para facilitar o desenvolvimento:

### Estrutura:

- `Dockerfile`: dentro da pasta `.docker/`
- `entrypoint.sh`: também dentro de `.docker/`
- `docker-compose.yml`: pode ser executado da raiz do projeto

### Comando para rodar:

```bash
docker-compose -f .docker/docker-compose.yml up --build
```

ou, se estiver usando versões mais recentes do docker/docker-compose

```bash
docker compose -f .docker/docker-compose.yml up --build
```

Após subir o projeto, o banco já estará populado com dados fake:

- 2 usuários (um deles: `admin@matera.com` / senha: `12345678`)
- Diversos empréstimos e pagamentos aleatórios gerados com Faker

---


## 📊 CI/CD

- CI com GitHub Actions:
  - Lint com `ruff`
  - Format com `black` e `isort`
  - Testes automáticos
  - Cobertura de testes verificada com `coverage` (pipeline falha se < 90%)

---

## 📘 Documentação e Endpoints

Documentação automática gerada com `drf-spectacular`, disponível em:

- Swagger: [`/api/docs/swagger/`](http://localhost:8000/api/docs/swagger/)
- Redoc: [`/api/docs/redoc/`](http://localhost:8000/api/docs/redoc/)

### Endpoints Disponíveis:

#### Accounts
- `GET /api/accounts/me/` → Obter dados da conta atual
- `POST /api/accounts/register/` → Registrar novo usuário

#### Auth
- `POST /api/auth/token/` → Obter token JWT
- `POST /api/auth/refresh/` → Renovar token JWT

#### Loans
- `GET /api/loans/` → Listar empréstimos
- `POST /api/loans/` → Criar empréstimo
- `GET /api/loans/{id}/` → Obter detalhes
- `PUT /api/loans/{id}/` → Atualizar empréstimo
- `PATCH /api/loans/{id}/` → Atualizar parcialmente
- `DELETE /api/loans/{id}/` → Deletar empréstimo

#### Payments
- `GET /api/payments/` → Listar pagamentos
- `POST /api/payments/` → Criar pagamento
- `GET /api/payments/{id}/` → Detalhar pagamento
- `PUT /api/payments/{id}/` → Atualizar pagamento
- `PATCH /api/payments/{id}/` → Atualizar parcialmente
- `DELETE /api/payments/{id}/` → Remover pagamento

---


## 🚀 Visualizar cobertura de testes com `coverage`

```bash
coverage run manage.py test
coverage report -m
```

Para gerar um HTML:

```bash
coverage html
```

Depois abra `htmlcov/index.html` no seu navegador.

