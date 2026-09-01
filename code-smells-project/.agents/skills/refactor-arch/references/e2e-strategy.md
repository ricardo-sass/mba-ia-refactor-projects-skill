# Estratégia De Testes E2E

Validar a aplicação como caixa-preta antes e depois da refatoração. Reutilizar a mesma suíte e os mesmos dados para tornar a comparação defensável.

## Momento De Execução

Durante as fases 1 e 2, apenas descobrir contratos e planejar a suíte. Não criar arquivos de teste nem infraestrutura.

Depois da aprovação explícita para a Fase 3:

1. Criar ou completar a estrutura de testes E2E sem alterar código da aplicação.
2. Preparar ambiente e seed isolados.
3. Executar a suíte contra o código original e salvar a linha de base.
4. Corrigir a estrutura de testes até distinguir falha do teste de defeito real.
5. Refatorar somente depois de registrar a linha de base.
6. Reconstruir o ambiente a partir de estado limpo.
7. Executar exatamente a mesma suíte, com os mesmos cenários e expectativas, contra o código refatorado.
8. Confirmar que os cenários de reprodução de defeitos falham antes e passam depois com a expectativa de correção já definida na linha de base.
9. Comparar resultados e registrar regressões, correções e itens não executados.
10. Encerrar processos, containers, redes e volumes exclusivos de teste.

## Seleção Do Executor

Priorizar:

1. runner e convenções já usados pelo projeto;
2. cliente HTTP do ecossistema da stack;
3. runner externo de contrato quando já declarado;
4. ferramenta mínima compatível com o runtime existente.

Não impor pytest, Jest, Newman ou outra ferramenta a toda codebase. Evitar dependência nova quando o runtime padrão já oferecer cliente e assertions suficientes.

## Isolamento

- Usar banco, schema, namespace, fila, bucket e cache exclusivos de teste.
- Tornar migrations e seed determinísticos e idempotentes.
- Bloquear chamadas para SMTP, pagamento, webhooks e serviços reais; usar stubs ou implementações falsas.
- Não reutilizar credenciais, volumes ou endpoints de produção.
- Escolher portas configuráveis ou efêmeras para evitar colisões.
- Não apagar recursos que não tenham sido criados pela própria execução.

## Evidências

Salvar em `reports/`:

- `e2e-baseline-<project>.md`: ambiente, comandos, cenários e resultados anteriores;
- `e2e-after-<project>.md`: mesma matriz depois da refatoração;
- logs relevantes sem segredos;
- diferenças de contrato e justificativas autorizadas.

Usar `PASSOU`, `FALHOU` ou `NÃO EXECUTADO`. Não converter indisponibilidade de Docker, dependência ou porta em sucesso.

## Critérios De Conclusão

- Todos os contratos invariantes passam antes e depois.
- Defeitos reproduzidos antes deixam de ser exploráveis depois.
- Nenhuma expectativa foi relaxada apenas para aprovar a versão refatorada.
- O banco e as integrações começam de estado conhecido em cada rodada.
- A aplicação fica realmente pronta antes dos testes, usando health/readiness check.
- O relatório permite reproduzir cada comando e resultado.
