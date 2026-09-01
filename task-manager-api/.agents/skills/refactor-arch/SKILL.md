---
name: refactor-arch
description: Analisar projetos backend, auditar arquitetura, segurança, SOLID e qualidade, gerar relatórios em português do Brasil com severidade e localização exata, organizar domínios nas pastas Models, Views/Routes e Controllers do MVC tradicional, adicionar Services e Repositories somente quando necessários e validar contratos E2E antes/depois com Docker Compose ou executor compatível. Usar quando o usuário pedir análise arquitetural, detecção de code smells ou anti-patterns, separação de domínios nas camadas MVC, auditoria de APIs, migração ou reorganização para MVC tradicional, modernização de APIs obsoletas ou validação de refatoração em diferentes tecnologias backend.
---

# Refatorar Arquitetura

Executar as fases em ordem. Não modificar arquivos da aplicação durante as fases 1 e 2; criar apenas o relatório obrigatório da auditoria. Tratar o projeto atual como raiz, ignorar dependências geradas e preservar contratos públicos, dados e comportamento observável.

## Idioma Dos Artefatos

Produzir em português do Brasil todo artefato textual gerado pela skill, incluindo análises, relatórios, títulos, tabelas, descrições de achados, recomendações, planos, checklists, mensagens de confirmação e resumos de validação. Usar ortografia, acentuação e terminologia próprias de pt-BR.

Preservar sem tradução:

- os nomes obrigatórios `refactor-arch` e `SKILL.md`;
- as severidades `CRITICAL`, `HIGH`, `MEDIUM` e `LOW`;
- a sigla `MVC` e os nomes arquiteturais obrigatórios `Models`, `Views/Routes` e `Controllers` quando citados como termos do enunciado;
- caminhos, nomes de arquivos, comandos, URLs, métodos HTTP, campos de API e demais contratos externos;
- identificadores de código e nomes oficiais de linguagens, frameworks, bibliotecas e APIs.

Traduzir todo o restante. Não reproduzir títulos ou textos explicativos em inglês apenas porque aparecem assim em exemplos ou ferramentas. Ao citar literalmente uma mensagem externa necessária como evidência, manter o original e acrescentar a explicação em pt-BR.

## Fase 1 - Analisar

1. Ler manifestos, pontos de entrada, configuração, rotas, modelos, testes e documentação.
2. Detectar linguagem, versão quando verificável, framework, banco, domínio e arquitetura atual conforme [project-analysis.md](references/project-analysis.md).
3. Ler [architecture-principles.md](references/architecture-principles.md), classificar a necessidade como MVC essencial, MVC com Services/Repositories ou MVC separado por domínios e identificar capacidades de negócio coesas, sempre com evidências.
4. Mapear para cada capacidade suas routes/views, controllers, services, models, repositories, integrações e dependências com outros domínios. Não tratar automaticamente cada entidade como um domínio.
5. Ler [contract-discovery.md](references/contract-discovery.md) e mapear contratos, comandos de inicialização, testes existentes, integrações externas e persistência.
6. Inventariar Dockerfile, Compose, CI, healthchecks, migrations, seeds e capacidades de isolamento, sem criar ou editar arquivos.
7. Contar apenas arquivos-fonte analisados; não estimar silenciosamente.
8. Imprimir o resumo `FASE 1: ANÁLISE DO PROJETO` definido em [report-template.md](references/report-template.md).

## Fase 2 - Auditar

1. Ler [anti-pattern-catalog.md](references/anti-pattern-catalog.md) por completo.
2. Cruzar os sinais do catálogo com evidências reais do projeto. Não criar achado sem evidência.
3. Auditar SRP, OCP, LSP, ISP, DIP, responsabilidades MVC, dependências entre camadas e mistura de vários domínios sem separação interna conforme [architecture-principles.md](references/architecture-principles.md).
4. Verificar APIs obsoletas nas versões declaradas; confirmar por documentação local, avisos de teste/análise estática ou documentação oficial quando houver acesso.
5. Atribuir severidade por impacto e possibilidade de exploração, não por quantidade de linhas.
6. Definir o menor perfil arquitetural capaz de corrigir os achados: MVC essencial, MVC com Services/Repositories ou MVC separado por domínios dentro de cada camada.
7. Manter `models/`, `views/` ou `routes/` e `controllers/` como pastas principais. Quando houver capacidades independentes, criar subpastas de domínio correspondentes dentro de cada camada; não criar uma pasta `modules/`.
8. Ler [e2e-strategy.md](references/e2e-strategy.md) e [containerization-guidelines.md](references/containerization-guidelines.md), então incluir um plano E2E genérico baseado nos contratos e capacidades detectados.
9. Informar arquivo e linha exatos. Separar ocorrências independentes; agrupar repetições mecânicas quando a causa e a correção forem as mesmas.
10. Salvar o relatório em `reports/audit-<project>.md`, usando [report-template.md](references/report-template.md), e ordenar achados por `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`.
11. Encerrar a fase com `Fase 2 concluída. Prosseguir com a refatoração (Fase 3)? [s/n]`, interromper a execução e aguardar uma nova resposta do usuário.

## Gate Obrigatório Entre As Fases 2 E 3

Exigir aprovação explícita do usuário depois que ele receber o relatório da Fase 2. Não iniciar a Fase 3 no mesmo turno em que o relatório e a pergunta de confirmação forem apresentados.

Aceitar como aprovação somente uma resposta afirmativa, direta e inequívoca do usuário, como `sim`, `s`, `aprovo` ou `pode prosseguir com a Fase 3`. Não inferir aprovação a partir de:

- pedido inicial para analisar, auditar, refatorar ou executar o desafio completo;
- autorização genérica ou antecipada fornecida antes da apresentação do relatório;
- silêncio, ausência de objeção, modo automático ou instrução para continuar trabalhando;
- aprovação concedida para outro projeto, outra execução ou outra versão do relatório.

Tratar cada projeto como uma aprovação independente. Aceitar uma única resposta para vários projetos somente quando o usuário identificar explicitamente todos eles. Se o relatório mudar de forma material depois da aprovação, apresentar a versão atualizada e solicitar nova aprovação.

Se a resposta for ambígua, pedir confirmação novamente e continuar aguardando. Se for negativa, encerrar depois de informar o caminho do relatório. Não criar, editar, mover ou excluir código da aplicação antes da resposta afirmativa explícita. Após recebê-la, registrar a aprovação no relatório e somente então iniciar a Fase 3.

## Fase 3 - Refatorar

1. Confirmar que o relatório registra a resposta afirmativa explícita do usuário para este projeto e esta versão da auditoria.
2. Ler [mvc-guidelines.md](references/mvc-guidelines.md), [architecture-principles.md](references/architecture-principles.md), [refactoring-playbook.md](references/refactoring-playbook.md), [contract-discovery.md](references/contract-discovery.md), [e2e-strategy.md](references/e2e-strategy.md) e [containerization-guidelines.md](references/containerization-guidelines.md).
3. Criar ou completar a estrutura de testes E2E sem alterar código da aplicação. Reutilizar ferramentas existentes e gerar infraestrutura específica da tecnologia somente quando necessário.
4. Executar testes existentes e E2E contra o código original. Salvar `reports/e2e-baseline-<project>.md` antes de refatorar.
5. Se a linha de base não puder ser executada, interromper, registrar o motivo e pedir decisão explícita antes de prosseguir sem essa proteção.
6. Planejar mudanças por achado e preservar URLs, métodos HTTP, status, formatos de resposta, esquema de dados e comandos documentados, salvo autorização explícita para quebra.
7. Aplicar o perfil aprovado: manter routes/views finas, controllers responsáveis pelo fluxo, Services para regras/orquestrações reutilizáveis e Models/Repositories para dados e persistência.
8. Criar as pastas principais `models/`, `views/` ou `routes/` e `controllers/`. Quando houver mais de uma capacidade coesa, separar cada domínio em subpastas correspondentes dentro dessas camadas e também dentro de `services/` e `repositories/`, caso existam. Não criar `modules/`.
9. Fazer a direção principal seguir `route/view -> controller -> service -> model/repository`, permitindo atalhos apenas quando a camada intermediária não possuir responsabilidade real.
10. Extrair segredos para o ambiente, parametrizar consultas, centralizar erros e validar entradas nos limites da aplicação.
11. Atualizar ou adicionar testes unitários, de integração e de arquitetura focados nos riscos corrigidos.
12. Refatorar incrementalmente e executar formatadores, análise estática e testes após cada grupo coerente de mudanças.
13. Reconstruir um ambiente limpo e executar exatamente a mesma suíte E2E contra o código refatorado.
14. Salvar `reports/e2e-after-<project>.md`, comparar com a linha de base e corrigir regressões dentro do escopo.
15. Encerrar somente recursos de teste criados pela execução.
16. Imprimir `FASE 3: REFATORAÇÃO CONCLUÍDA` com arquitetura adotada, domínios distribuídos nas camadas MVC, nova estrutura, achados tratados e resultados antes/depois.

## Regras De Decisão

- Adaptar a estrutura ao framework; aplicar responsabilidades MVC, não nomes de pastas cegamente.
- Organizar primeiro pelas camadas MVC `models`, `views/routes` e `controllers`; separar domínios por subpastas dentro de cada camada quando houver múltiplas capacidades coesas.
- Não criar `modules/` como contêiner da arquitetura-alvo.
- Manter em `shared` apenas componentes técnicos ou conceitos estáveis realmente compartilhados. Não usá-lo como destino para código sem proprietário.
- Não equiparar tabela, endpoint ou entidade a domínio. Delimitar áreas de negócio por linguagem, regras, fluxos, consistência e ritmo de mudança.
- Tratar os projetos fornecidos como referências de validação, nunca como fonte de endpoints, entidades ou caminhos fixos para outros projetos.
- Aplicar SOLID sem criar interfaces ou camadas vazias apenas por formalidade.
- Preferir Docker Compose para E2E quando ele oferecer isolamento reproduzível; usar execução nativa isolada quando for mais apropriada.
- Preferir recursos nativos e dependências já instaladas. Adicionar dependência apenas quando reduzir risco de segurança ou complexidade de forma justificável.
- Não mascarar ausência de teste. Distinguir `passou`, `falhou` e `não executado`.
- Não afirmar `zero anti-patterns` sem repetir a auditoria e apresentar a evidência.
- Preservar alterações preexistentes do usuário e evitar refatorações fora dos achados aprovados.
- Interromper antes de operações destrutivas, migrações irreversíveis ou mudanças de contrato não autorizadas.
