# E2E Após Refatoração - ecommerce-api-legacy

- **Modo:** after
- **Executor:** Node.js v24.12.0 com fetch nativo
- **Comando:** E2E_MODE=after E2E_REPORT=reports/e2e-after-ecommerce-api-legacy.md node tests/e2e/run-e2e.js
- **Ambiente:** execução nativa isolada em http://127.0.0.1:3000 com SQLite em memória
- **Resumo:** PASSOU=7; FALHOU=0; NÃO EXECUTADO=0

| Cenário | Resultado | Evidência |
|---|---|---|
| Checkout aprovado preserva contrato | PASSOU | Expectativas atendidas |
| Checkout recusado preserva contrato | PASSOU | Expectativas atendidas |
| Curso ausente preserva contrato | PASSOU | Expectativas atendidas |
| Payload inválido preserva contrato | PASSOU | Expectativas atendidas |
| Relatório financeiro preserva schema | PASSOU | Expectativas atendidas |
| Exclusão preserva resposta textual | PASSOU | Expectativas atendidas |
| Logs não expõem cartão nem chave | PASSOU | Expectativas atendidas |

## Logs capturados (dados sensíveis mascarados)

```text
[INFO] LMS API rodando {"port":3000}
[INFO] Processando pagamento {"courseId":2}
[INFO] Processando pagamento {"courseId":1}
```
