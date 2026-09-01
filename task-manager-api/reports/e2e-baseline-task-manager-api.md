# Linha de Base E2E — task-manager-api

## Estado

**PASSOU** — todos os 23 cenários invariantes passaram no código original. Os 7 cenários de reprodução de defeito falharam conforme a expectativa segura definida antes da refatoração, comprovando os problemas sem tratá-los como contratos a preservar.

## Ambiente

- **Data:** 25/08/2026
- **Runtime:** `venv/bin/python` — Python 3.12.3
- **Aplicação:** cópia do código original em diretório temporário exclusivo
- **Persistência:** SQLite criado e populado dentro da cópia temporária
- **Executor:** cliente WSGI do Flask, no limite HTTP request/response
- **Integrações externas:** nenhuma integração foi acionada; NotificationService não está conectado às Routes
- **Limpeza:** o diretório temporário e seu banco foram removidos automaticamente ao final

O executor HTTP por socket foi tentado primeiro, mas o sandbox recusou `socket()` com `PermissionError: [Errno 1] Operation not permitted`. Isso foi classificado como indisponibilidade do executor, não como falha da aplicação. A suíte foi então executada pelo cliente WSGI do próprio Flask, preservando request, roteamento, response, serialização e persistência isolada.

## Comandos

```bash
venv/bin/python -m py_compile tests/e2e/run_contracts.py
venv/bin/python tests/e2e/run_contracts.py \
  --stage baseline \
  --json-output /tmp/task-manager-e2e-baseline.json
```

## Resultado resumido

| Tipo | PASSOU | FALHOU | Interpretação |
|---|---:|---:|---|
| Invariantes | 23 | 0 | contratos preserváveis confirmados |
| Reprodução de defeitos | 0 | 7 | vulnerabilidades/erros confirmados no original |
| **Total** | **23** | **7** | linha de base apta para refatoração |

## Cenários invariantes

| Cenário | Resultado |
|---|---|
| raiz | PASSOU |
| health | PASSOU |
| login válido | PASSOU |
| login inválido | PASSOU |
| listagem de tasks | PASSOU |
| detalhe de task | PASSOU |
| task ausente | PASSOU |
| busca de tasks | PASSOU |
| estatísticas de tasks | PASSOU |
| listagem de usuários | PASSOU |
| detalhe de usuário | PASSOU |
| tasks do usuário | PASSOU |
| resumo de relatórios | PASSOU |
| relatório por usuário | PASSOU |
| listagem de categorias | PASSOU |
| criação de categoria | PASSOU |
| atualização de categoria | PASSOU |
| criação de usuário | PASSOU |
| criação de task associada | PASSOU |
| atualização de task | PASSOU |
| exclusão de task | PASSOU |
| exclusão de usuário | PASSOU |
| exclusão de categoria | PASSOU |

## Reprodução de defeitos

| Cenário | Resultado | Evidência observada |
|---|---|---|
| login não expõe senha | FALHOU | `password` presente em `user` |
| filtro numérico inválido | FALHOU | `GET /tasks/search?priority=abc` retornou 500 HTML |
| detalhe não expõe senha | FALHOU | `GET /users/1` devolveu `password` |
| mutação anônima bloqueada | FALHOU | `POST /tasks` anônimo retornou 201 e persistiu |
| token forjado bloqueado | FALHOU | token previsível forjado foi ignorado e a Task foi criada |
| criação não expõe senha | FALHOU | usuário criado continuou expondo `password` |
| body inválido retorna JSON 400 | FALHOU | array JSON em `POST /tasks` retornou 500 HTML |

## Critério para a execução posterior

A mesma suíte e as mesmas expectativas serão executadas após a refatoração. A conclusão exige:

- os 23 invariantes ainda em `PASSOU`;
- os 7 cenários de reprodução corrigidos em `PASSOU`;
- nenhuma expectativa relaxada ou removida;
- novo SQLite iniciado a partir de estado limpo.
