# Validação E2E — Código Refatorado

## Ambiente

- **Projeto:** `code-smells-project`
- **Versão avaliada:** código refatorado após aprovação explícita `s`
- **Executor:** exatamente a mesma suíte `unittest` com `Flask.test_client()` usada na linha de base
- **Runtime:** Python 3.12.3, Flask 3.1.1 e SQLite
- **Isolamento:** um diretório temporário e um arquivo SQLite exclusivo por teste; nenhum `loja.db` do projeto foi criado ou reutilizado
- **Docker Compose:** não utilizado; a execução nativa permaneceu suficiente e reproduzível
- **Integrações externas:** nenhuma chamada real

## Comando E2E reproduzido

```bash
venv/bin/python -m unittest discover -v -s tests/e2e -p 'test_*.py'
```

## Resultado geral

**PASSOU** — 16 testes executados em 3,536 s: 16 passaram e nenhum falhou. O executor terminou com código 0.

## Matriz de comparação

| Cenário | Tipo | Antes | Depois |
|---|---|---|---|
| Contratos de `/` e `/health` | Invariante | PASSOU | PASSOU |
| CRUD e busca de produtos | Invariante | PASSOU | PASSOU |
| Validação básica de produto e recursos ausentes | Invariante | PASSOU | PASSOU |
| Criação e login de usuário | Invariante | PASSOU | PASSOU |
| Pedido, listagens, status aprovado e relatório | Invariante | PASSOU | PASSOU |
| Console SQL não público | Reprodução de defeito F-001 | FALHOU | PASSOU |
| Reset do banco não público | Reprodução de defeito F-005 | FALHOU | PASSOU |
| Login resistente a injeção SQL | Reprodução de defeito F-002 | FALHOU | PASSOU |
| Apóstrofos persistidos literalmente | Reprodução de defeito F-002 | FALHOU | PASSOU |
| Senha com hash e ausente das respostas | Reprodução de defeito F-004 | FALHOU | PASSOU |
| Health sem segredo/caminho interno | Reprodução de defeito F-003 | FALHOU | PASSOU |
| JSON inválido como erro do cliente | Reprodução de defeito F-013/F-015 | FALHOU | PASSOU |
| Quantidades não positivas/duplicadas sem alterar estoque | Reprodução de defeito F-008/F-013 | FALHOU | PASSOU |
| Cancelamento restaura estoque uma vez e ID ausente retorna 404 | Reprodução de defeito F-009 | FALHOU | PASSOU |
| Produto referenciado não pode ser excluído | Reprodução de defeito F-014 | FALHOU | PASSOU |
| Debug desabilitado e CORS restrito | Reprodução de defeito F-006/F-016 | FALHOU | PASSOU |

## Validações complementares

Comando:

```bash
venv/bin/python -m unittest discover -v
```

**PASSOU** — 30 testes em 4,341 s: 16 E2E, 5 de arquitetura, 4 de integração e 5 unitários.

- A transação de pedido foi interrompida por trigger controlada no segundo item; pedido, itens e estoque sofreram rollback integral.
- A listagem de múltiplos pedidos executou uma única consulta `SELECT`, eliminando N+1.
- A conexão SQLite foi fechada no fim do contexto da aplicação.
- Uma senha legada em texto puro foi migrada para hash após autenticação válida.
- As fronteiras MVC impedem SQL em Routes/Controllers/Services, HTTP em Models/Repositories e dependências diretas de banco nos Controllers.
- A análise por AST passou em 62 arquivos Python e `git diff --check` não encontrou erros de whitespace.

## Contratos e correções

- As 17 operações legítimas foram preservadas com os mesmos métodos e caminhos.
- `POST /admin/query` e `POST /admin/reset-db` agora retornam 404 porque foram removidos como correção autorizada das vulnerabilidades F-001 e F-005.
- Campos legítimos, schemas principais e status invariantes cobertos pela suíte não regrediram.
- Respostas que continham `senha`, `secret_key` e `db_path` foram reduzidas deliberadamente para eliminar exposição sensível.
- Entradas antes vulneráveis ou inválidas agora recebem 4xx sem detalhes internos.
- Cancelamento e exclusão referenciada mudaram deliberadamente para preservar estoque e integridade.

## Recursos e riscos restantes

- Todos os arquivos/bancos temporários foram removidos pela própria suíte; nenhum `loja.db` apareceu no projeto.
- Bancos novos recebem FKs, constraints e senhas de seed com hash. Para um `loja.db` legado já existente, a aplicação protege os fluxos HTTP e migra a senha no login, mas a reconstrução física das tabelas para incorporar todas as constraints ainda requer backup e migration operacional específica.
- O comando `python app.py` permanece destinado ao desenvolvimento, agora com debug desabilitado e bind local por padrão; um servidor WSGI de produção deve ser escolhido no ambiente de implantação.

## Conclusão

**Regressões de contrato:** nenhuma nos invariantes cobertos.

**Defeitos reproduzidos:** 11 falhavam antes e passaram depois com as mesmas expectativas.
