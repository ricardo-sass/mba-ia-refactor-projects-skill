# E2E Baseline - ecommerce-api-legacy

- **Modo:** baseline
- **Executor:** Node.js v24.12.0 com fetch nativo
- **Comando:** E2E_MODE=baseline E2E_REPORT=reports/e2e-baseline-ecommerce-api-legacy.md node tests/e2e/run-e2e.js
- **Ambiente:** execução nativa isolada em http://127.0.0.1:3000 com SQLite em memória
- **Resumo:** PASSOU=6; FALHOU=1; NÃO EXECUTADO=0

| Cenário | Resultado | Evidência |
|---|---|---|
| Checkout aprovado preserva contrato | PASSOU | Expectativas atendidas |
| Checkout recusado preserva contrato | PASSOU | Expectativas atendidas |
| Curso ausente preserva contrato | PASSOU | Expectativas atendidas |
| Payload inválido preserva contrato | PASSOU | Expectativas atendidas |
| Relatório financeiro preserva schema | PASSOU | Expectativas atendidas |
| Exclusão preserva resposta textual | PASSOU | Expectativas atendidas |
| Logs não expõem cartão nem chave | FALHOU | cartão completo exposto |

## Logs capturados (dados sensíveis mascarados)

```text
Frankenstein LMS rodando na porta 3000...
Processando cartão [CARTÃO_MASCARADO] na chave [SEGREDO_MASCARADO]
[LOG] Salvando no cache: last_checkout_2
Processando cartão [CARTÃO_MASCARADO] na chave [SEGREDO_MASCARADO]
```
