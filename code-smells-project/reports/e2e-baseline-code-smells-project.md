# Linha de Base E2E — Código Original

## Ambiente

- **Projeto:** `code-smells-project`
- **Versão avaliada:** código original anterior à refatoração aprovada
- **Executor:** `unittest` com `Flask.test_client()`
- **Runtime:** Python 3.12.3, Flask 3.1.1 e SQLite
- **Isolamento:** um diretório temporário e um arquivo SQLite exclusivo por teste; nenhum `loja.db` do projeto foi criado ou reutilizado
- **Docker Compose:** não utilizado; a execução nativa oferece isolamento suficiente para a dependência SQLite local
- **Integrações externas:** nenhuma chamada real; as notificações atuais são apenas saídas `print`

## Comando

```bash
venv/bin/python -m unittest discover -v -s tests/e2e -p 'test_*.py'
```

## Resultado geral

**FALHOU** — 16 testes executados em 0,586 s: 5 passaram e 11 falharam. O executor terminou com código 1 devido às expectativas de correção dos defeitos reproduzidos; a infraestrutura e os cenários invariantes foram executados normalmente.

## Matriz de cenários

| Cenário | Tipo | Resultado antes | Evidência |
|---|---|---|---|
| Contratos de `/` e `/health` | Invariante | PASSOU | status, versão, banco e contagens válidos |
| CRUD e busca de produtos | Invariante | PASSOU | criar, consultar, atualizar, buscar e excluir preservam schemas/status principais |
| Validação básica de produto e recursos ausentes | Invariante | PASSOU | entrada inválida retorna 400; produto/usuário ausentes retornam 404 |
| Criação e login de usuário | Invariante | PASSOU | criação 201, login válido 200 e senha incorreta 401 |
| Pedido, listagens, status aprovado e relatório | Invariante | PASSOU | pedido 201, leitura por usuário/global, atualização 200 e relatório coerente |
| Console SQL não público | Reprodução de defeito F-001 | FALHOU | `POST /admin/query` retornou 200 em vez de 401/403/404 |
| Reset do banco não público | Reprodução de defeito F-005 | FALHOU | `POST /admin/reset-db` retornou 200 e removeu os dados |
| Login resistente a injeção SQL | Reprodução de defeito F-002 | FALHOU | payload de injeção autenticou e retornou 200 em vez de 401 |
| Apóstrofos persistidos literalmente | Reprodução de defeito F-002 | FALHOU | criação retornou 500 com erro de sintaxe SQL |
| Senha com hash e ausente das respostas | Reprodução de defeito F-004 | FALHOU | listagem ainda contém o campo `senha`; armazenamento permanece recuperável |
| Health sem segredo/caminho interno | Reprodução de defeito F-003 | FALHOU | resposta contém `secret_key` e `db_path` e a aplicação usa a chave fixa |
| JSON inválido como erro do cliente | Reprodução de defeito F-013/F-015 | FALHOU | `null` em `/login` retornou 500 em vez de 400 |
| Quantidades não positivas/duplicadas sem alterar estoque | Reprodução de defeito F-008/F-013 | FALHOU | quantidade negativa foi aceita com 201 |
| Cancelamento restaura estoque uma vez e ID ausente retorna 404 | Reprodução de defeito F-009 | FALHOU | estoque permaneceu reduzido após cancelamento |
| Produto referenciado não pode ser excluído | Reprodução de defeito F-014 | FALHOU | exclusão retornou 200 e deixou referência órfã |
| Debug desabilitado e CORS restrito | Reprodução de defeito F-006/F-016 | FALHOU | `application.debug` permaneceu verdadeiro |

## Diagnóstico da linha de base

- A suíte distingue falhas do executor de defeitos reais: os cinco cenários invariantes passaram e as onze falhas correspondem aos achados aprovados.
- O banco temporário foi criado e removido por cada teste; não restaram recursos de execução.
- Nenhuma expectativa será relaxada depois da refatoração. A mesma suíte e o mesmo comando serão reutilizados.
- Como a linha de base foi executável e reproduzível, a refatoração pode prosseguir com esta proteção.
