# Validação E2E Após Refatoração — task-manager-api

## Estado

**PASSOU** — os 30 cenários da mesma suíte usada na linha de base passaram em ambiente reconstruído e limpo: 23 contratos invariantes foram preservados e os 7 defeitos reproduzidos no código original deixaram de ser exploráveis.

## Ambiente

- **Data:** 25/08/2026
- **Runtime:** `venv/bin/python` — Python 3.12.3
- **Aplicação:** cópia limpa do código refatorado em diretório temporário exclusivo
- **Persistência:** SQLite novo, criado e populado dentro da cópia
- **Executor:** cliente WSGI do Flask, no limite HTTP request/response
- **Configuração:** segredo de teste efêmero, sem credenciais externas
- **Integrações externas:** nenhuma conexão SMTP ou de rede externa
- **Limpeza:** cópia, banco e recursos temporários removidos ao final

## Comandos

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python \
  -W error::DeprecationWarning \
  -m unittest discover -s tests -p 'test*.py' -v

PYTHONDONTWRITEBYTECODE=1 venv/bin/python \
  tests/e2e/run_contracts.py \
  --stage after \
  --json-output /tmp/task-manager-e2e-after-final.json

venv/bin/pip check
git diff --check
```

## Resultado resumido

| Verificação | Resultado | Evidência |
|---|---|---|
| Unitários, integração e arquitetura | PASSOU | 18 testes |
| Contratos invariantes E2E | PASSOU | 23 de 23 |
| Correções de defeitos E2E | PASSOU | 7 de 7 |
| Total E2E | PASSOU | 30 de 30 |
| DeprecationWarning como erro | PASSOU | suíte completa sem warning |
| Dependências instaladas | PASSOU | `No broken requirements found.` |
| Integridade do diff | PASSOU | `git diff --check` sem saída |

## Comparação com a linha de base

| Cenário | Antes | Depois | Classificação |
|---|---|---|---|
| 23 invariantes de raiz, health, login, CRUD, busca, estatísticas e relatórios | PASSOU | PASSOU | contrato preservado |
| login não expõe senha | FALHOU | PASSOU | F-001 corrigido |
| filtro numérico inválido | FALHOU, 500 HTML | PASSOU, 400 JSON | F-008/F-009 corrigidos |
| detalhe não expõe senha | FALHOU | PASSOU | F-001 corrigido |
| mutação anônima bloqueada | FALHOU, 201 | PASSOU, 401 | F-003 corrigido |
| token forjado bloqueado | FALHOU, 201 | PASSOU, 401 | F-003 corrigido |
| criação não expõe senha | FALHOU | PASSOU | F-001 corrigido |
| body inválido retorna JSON 400 | FALHOU, 500 HTML | PASSOU, 400 JSON | F-008/F-009 corrigidos |

## Mudanças de segurança intencionais

- Todos os endpoints de domínio agora exigem `Authorization: Bearer <token>`; apenas `/`, `/health` e `/login` permanecem públicos.
- Categorias e relatórios exigem `admin` ou `manager`; criação/exclusão de usuários exige `admin`; atualização de usuário exige o próprio usuário ou `admin`.
- O campo `password` foi removido de todas as respostas públicas.
- Tokens passaram a ser assinados e possuir expiração configurável.
- Novas senhas exigem oito caracteres e usam password hashing adaptativo; MD5 existe somente para verificar e migrar registros legados no primeiro login válido.

Essas diferenças correspondem às correções de segurança explicitamente aprovadas no relatório de auditoria. Nenhum caminho, método HTTP ou campo não sensível coberto pelos invariantes foi removido ou renomeado.

## Regressões

Nenhuma regressão foi observada nos 23 contratos invariantes. A suíte posterior reutilizou os mesmos dados, cenários e expectativas da linha de base; nenhuma expectativa foi relaxada.
