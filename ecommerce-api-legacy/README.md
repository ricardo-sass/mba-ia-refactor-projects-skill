# ecommerce-api-legacy

LMS API (com fluxo de checkout) em Node.js/Express usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
npm install
ADMIN_TOKEN=troque-este-token npm start
```

A aplicação sobe em `http://localhost:3000`. O banco SQLite é em memória e já carrega seeds automaticamente no boot.

As operações `GET /api/admin/financial-report` e `DELETE /api/users/:id` exigem o header `Authorization: Bearer <ADMIN_TOKEN>`. A porta e o arquivo SQLite podem ser configurados por `PORT` e `SQLITE_FILENAME`.

## Testes

```bash
npm test
npm run test:e2e
```

Exemplos de requisições estão em `api.http`.
