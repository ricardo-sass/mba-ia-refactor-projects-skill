# Descoberta De Contratos

Descobrir contratos sem codificar conhecimento prévio do projeto. Usar a primeira fonte confiável disponível e cruzar fontes quando divergirem.

## Ordem De Evidência

1. Especificações OpenAPI, AsyncAPI, GraphQL schema, Protobuf ou equivalentes.
2. Testes de contrato, integração ou E2E existentes.
3. Collections Postman/Insomnia e arquivos `.http`.
4. Documentação pública e exemplos executáveis.
5. Declarações de routes/controllers e schemas de entrada/saída.
6. Inferência controlada a partir do código, marcada como inferência.

## Inventário Por Operação

Registrar:

- protocolo, método e caminho/operação;
- autenticação e autorização;
- headers, parâmetros, body e tipos;
- status e formato de resposta;
- efeitos persistentes e idempotência;
- integrações externas acionadas;
- campos dinâmicos, como IDs, datas e tokens;
- dados ou pré-condições necessários.

Não traduzir nem renomear campos, rotas ou valores enumerados do contrato.

## Cenários

Derivar pelo menos:

- caminho principal;
- entrada inválida e recurso ausente;
- autenticação/autorização quando aplicável;
- repetição/idempotência quando relevante;
- falha de integração externa;
- consistência de escrita multi-etapas;
- vulnerabilidade associada a cada achado de segurança.

Separar os cenários em:

- **Invariantes:** devem passar antes e depois da refatoração.
- **Caracterização:** registram comportamento observado que precisa de decisão antes de ser alterado.
- **Reprodução de defeito:** demonstram falha antes e correção depois; não exigir que a vulnerabilidade continue funcionando.

## Comparação Segura

Comparar sem tornar testes frágeis:

- validar schema e campos relevantes em vez de serialização textual completa;
- normalizar IDs, timestamps, tokens e ordem quando o contrato não a garantir;
- preservar status, headers e tipos;
- verificar efeitos pela API sempre que possível;
- consultar o banco diretamente apenas quando o efeito não for observável pelo contrato e documentar o motivo.

Quando fontes divergirem, registrar a divergência no relatório e pedir decisão no gate da Fase 2 se a escolha puder quebrar consumidores.
