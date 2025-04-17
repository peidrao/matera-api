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
- Logging automático ao pagar e quitar um empréstimo
- Throttling para evitar abusos na API
- Filtros com `django-filters`
- Documentação com `drf-spectacular`

---

## 🧪 Testes

- Testes unitários e de integração usando `unittest.TestCase`
- Cobertura ampla nos fluxos de pagamento e edição

---

## 🐳 Ambiente com Docker

Este projeto usa Docker para facilitar o desenvolvimento:

### Estrutura:
- `Dockerfile`: dentro da pasta `.docker/`
- `entrypoint.sh`: também dentro de `.docker/`
- `docker-compose.yml`: também movido para `.docker/`

### Comando para rodar:

```bash
docker-compose -f .docker/docker-compose.yml up --build
```

ou, se estiver usando versões mais recentes do docker/docker-compose

```bash
docker compose -f .docker/docker-compose.yml up --build
```

Após subir o projeto, o banco já estará populado com dados fake:

- 2 usuários (um deles: admin@matera.com / senha: 12345678)
- Diversos empréstimos e pagamentos aleatórios gerados com Faker


---

## ⚠️ Observabilidade

Inicialmente, foi feita uma tentativa de integrar o OpenTelemetry com o Django, visando capturar métricas, traces e logs de forma padronizada. Porém, enfrentei dificuldades técnicas com a instrumentação automática e compatibilidade com algumas dependências do projeto.

