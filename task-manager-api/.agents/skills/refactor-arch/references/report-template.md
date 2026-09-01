# Template De Relatório

Usar Markdown no arquivo persistido. Manter evidências curtas e acionáveis.

## Sumário

- Fase 1: resumo da análise
- Fase 2: relatório, arquitetura-alvo, plano E2E e confirmação
- Fase 3: resultado da refatoração e comparação E2E

```text
================================
FASE 1: ANÁLISE DO PROJETO
================================
Projeto:        <nome>
Linguagem:      <linguagem e versão verificada>
Framework:      <framework e versão verificada>
Dependências:   <dependências relevantes>
Banco de dados: <banco/camada de acesso>
Domínio:        <domínio>
Domínios MVC:   <domínios e subpastas correspondentes nas camadas>
Arquitetura:    <arquitetura atual>
Perfil MVC:     <essencial | com Services/Repositories | separado por domínios>
Contratos:      <fontes encontradas>
Execução E2E:   <Compose existente | Compose a gerar | nativa | indisponível>
Arquivos-fonte: <quantidade e critério>
Linhas-fonte:   <quantidade>
Ponto de entrada: <caminho>
Testes:         <comando ou não encontrado>
Inicialização:  <comando>
================================
```

```markdown
# Relatório de Auditoria de Arquitetura

## Projeto

- **Nome:** <nome>
- **Stack:** <linguagem + framework + banco de dados>
- **Escopo:** <arquivos e exclusões>
- **Linha de base:** <estado de testes/inicialização antes das mudanças>

## Resumo

| Severidade | Quantidade |
|---|---:|
| CRITICAL | 0 |
| HIGH | 0 |
| MEDIUM | 0 |
| LOW | 0 |
| **Total** | **0** |

## Achados

### F-001 - [CRITICAL] <título>

- **Localização:** `caminho/arquivo.ext:linha`
- **Categoria:** Segurança | Arquitetura | Confiabilidade | Desempenho | Manutenibilidade | Obsolescência
- **Evidência:** <comportamento específico do código, sem revelar o valor de um segredo>
- **Impacto:** <falha ou custo concreto>
- **Recomendação:** <correção direcionada>
- **Validação:** <teste que comprova a correção>

## Avaliação Arquitetural

- **Perfil MVC:** <essencial | com Services/Repositories | separado por domínios, com evidências>
- **Organização atual:** <por camadas | por camadas e domínios | híbrida>
- **Mapa de domínios:** <domínio -> models, views/routes, controllers, services e repositories próprios>
- **Dependências entre domínios:** <Services/funções públicas e violações encontradas>
- **SOLID:** <violações e princípios preservados>
- **Responsabilidades MVC:** <vazamentos entre Route/View, Controller, Service, Model e Repository>
- **Arquitetura-alvo:** <MVC essencial | MVC com Services/Repositories | MVC separado por domínios em cada camada>

## Plano De Validação E2E

- **Fontes de contrato:** <OpenAPI, testes, collection, documentação ou routes>
- **Executor:** <runner existente ou alternativa mínima>
- **Ambiente:** <Docker Compose ou execução nativa isolada>
- **Dependências:** <banco, cache, fila e stubs necessários>
- **Cenários invariantes:** <lista resumida>
- **Reprodução de defeitos:** <achados cobertos>
- **Artefatos:** `reports/e2e-baseline-<project>.md` e `reports/e2e-after-<project>.md`

## Escopo da Refatoração

<mapeamento ordenado dos achados para as mudanças propostas>

## Confirmação

Fase 2 concluída. Prosseguir com a refatoração (Fase 3)? [s/n]

**Status da aprovação:** aguardando resposta explícita do usuário.
```

Encerrar a execução depois de apresentar a pergunta. Não iniciar a Fase 3 no mesmo turno. Depois de receber uma resposta afirmativa explícita, atualizar o status para `aprovada explicitamente pelo usuário` e registrar a resposta recebida. Não registrar aprovação presumida ou inferida.

Quando uma ocorrência ocupar um intervalo, usar a primeira linha executável e citar linhas adicionais no texto. Não usar intervalo impreciso como substituto de evidência. A linha de base pode ser `não executado durante a auditoria`; não inventar resultado.

Ao concluir a fase 3, imprimir:

```text
================================
FASE 3: REFATORAÇÃO CONCLUÍDA
================================
Arquitetura adotada: <perfil e justificativa>
Domínios nas camadas MVC: <domínios, subpastas e responsabilidades>
Nova estrutura: <árvore>
Achados tratados: <identificadores>
Validação estática/unitária:
  PASSOU|FALHOU|NÃO EXECUTADO - <comando/verificação>
E2E antes: PASSOU|FALHOU|NÃO EXECUTADO - <relatório>
E2E depois: PASSOU|FALHOU|NÃO EXECUTADO - <relatório>
Regressões de contrato: <nenhuma | lista>
Riscos restantes: <itens ou nenhum observado>
================================
```
