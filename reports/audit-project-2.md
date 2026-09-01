# Relatório de Auditoria de Arquitetura

## Fase 1: análise do projeto

```text
================================
FASE 1: ANÁLISE DO PROJETO
================================
Projeto:        ecommerce-api-legacy (manifesto: desafio-arquitetura-ia-boilerplate)
Linguagem:      JavaScript em Node.js 24.12.0 verificado no ambiente; versão mínima não declarada
Framework:      Express 4.22.1 no package-lock.json (^4.18.2 no package.json)
Dependências:   Express 4.22.1 e sqlite3 5.1.7
Banco de dados: SQLite em memória, via callbacks do driver sqlite3
Domínio:        LMS/e-commerce de cursos, com checkout, matrícula, pagamento, usuários e relatório financeiro
Domínios MVC:   checkout (cursos, usuários, matrícula e pagamento transacionais), relatórios financeiros e gestão de usuários; atualmente todos estão em src/AppManager.js
Arquitetura:    monólito sem camadas; entry point separado, porém routes, fluxo, regras e SQL estão concentrados em AppManager
Perfil MVC:     separado por domínios, com Services/Repositories onde há transação ou consulta complexa
Contratos:      api.http, README.md e declarações de routes em src/AppManager.js
Execução E2E:   execução nativa isolada proposta, com SQLite temporário/em memória e cliente HTTP do Node.js
Arquivos-fonte: 3 arquivos JavaScript em src/ (excluídos .agents, dependências, relatórios e artefatos)
Linhas-fonte:   180 linhas físicas nos 3 arquivos-fonte
Ponto de entrada: src/app.js
Testes:         não encontrado
Inicialização:  npm start (node src/app.js)
================================
```

### Stack, infraestrutura e linha de base

- **Nome do manifesto:** `desafio-arquitetura-ia-boilerplate`; **nome do diretório e README:** `ecommerce-api-legacy`.
- **Persistência:** cinco tabelas criadas no boot (`users`, `courses`, `enrollments`, `payments`, `audit_logs`) e seed embutido em `src/AppManager.js:12` e `src/AppManager.js:18`.
- **Isolamento atual:** o banco `:memory:` nasce a cada processo. Isso favorece testes isolados, mas a aplicação não exporta uma factory ou o servidor, e a porta é fixa.
- **Docker/Compose/CI/healthcheck/migrations:** não encontrados. Não há migrations separadas; criação e seed estão acoplados ao boot.
- **Dependências instaladas:** ausentes no worktree; `npm ls --depth=0` retornou `ELSPROBLEMS`. Testes e inicialização não foram executados durante a auditoria.
- **Estado preexistente:** o índice Git contém uma refatoração anterior parcialmente adicionada/removida, enquanto o worktree expõe novamente os três arquivos legados. Esta auditoria considera o conteúdo efetivamente presente no worktree e não altera essas mudanças.

### Capacidades e contratos observados

| Capacidade | Entrada e contrato | Regras/efeitos | Proprietário atual | Dependências |
|---|---|---|---|---|
| Checkout | `POST /api/checkout`; JSON com `usr`, `eml`, `pwd`, `c_id`, `card`; `200` JSON `{ "msg": "Sucesso", "enrollment_id": number }`; erros textuais `400`, `404` ou `500` | Localiza curso ativo e usuário; cria usuário se necessário; aceita cartão iniciado por `4`; cria matrícula, pagamento e auditoria; atualiza cache | `src/AppManager.js:28` | cursos, usuários, matrículas, pagamentos, auditoria, configuração/cache |
| Relatório financeiro | `GET /api/admin/financial-report`; sem autenticação observável; `200` com array de `{ course, revenue, students: [{ student, paid }] }`; `500` textual no erro inicial | Agrega cursos, matrículas, usuários e pagamentos; soma somente pagamentos `PAID` em `revenue`, embora `paid` exponha o valor de qualquer status encontrado | `src/AppManager.js:80` | cursos, matrículas, usuários e pagamentos |
| Gestão de usuários | `DELETE /api/users/:id`; sem autenticação observável; resposta textual `200` | Exclui somente `users`, deixando relações dependentes | `src/AppManager.js:131` | usuários e, por integridade, matrículas/pagamentos |

Não há especificação OpenAPI nem testes. Tipos, autenticação, headers e idempotência não documentados foram marcados como não definidos, em vez de inferidos como garantias.

## Fase 2: auditoria

## Resumo

| Severidade | Quantidade |
|---|---:|
| CRITICAL | 2 |
| HIGH | 5 |
| MEDIUM | 6 |
| LOW | 2 |
| **Total** | **15** |

## Achados

### F-001 - [CRITICAL] Segredos operacionais embutidos no código

- **Localização:** `src/utils.js:2`
- **Categoria:** Segurança
- **Evidência:** configuração versionável contém usuário de banco, senha explícita e uma chave com aparência de produção nas linhas 2 a 4.
- **Impacto:** qualquer leitor do código ou artefato pode obter credenciais e acessar integrações; rotação e configuração por ambiente ficam inviáveis.
- **Recomendação:** revogar/rotacionar os valores, carregá-los de variáveis de ambiente e manter apenas exemplos inequivocamente fictícios em `.env.example`.
- **Validação:** busca por segredos não encontra valores reais; o boot falha de modo seguro quando credencial obrigatória não existe e funciona com credenciais de teste injetadas.

### F-002 - [CRITICAL] Número de cartão e chave de pagamento expostos em log

- **Localização:** `src/AppManager.js:45`
- **Categoria:** Segurança
- **Evidência:** o checkout registra o valor integral de `card` junto de `config.paymentGatewayKey`.
- **Impacto:** dados de pagamento e credencial podem persistir em logs e sistemas de observabilidade, ampliando comprometimento e exposição regulatória.
- **Recomendação:** nunca registrar PAN nem chave; usar log estruturado com identificador de correlação e, se indispensável, apenas metadados não sensíveis.
- **Validação:** executar checkout com marcadores exclusivos e confirmar que nenhum marcador sensível aparece na saída capturada.

### F-003 - [HIGH] Senhas armazenadas com transformação reversível e seed em texto puro

- **Localização:** `src/utils.js:17`
- **Categoria:** Segurança
- **Evidência:** `badCrypto` repete Base64 e trunca o resultado; o seed grava senha literal em `src/AppManager.js:18`.
- **Impacto:** senhas são recuperáveis ou trivialmente atacáveis em caso de leitura do banco, permitindo tomada de contas e reutilização de credenciais.
- **Recomendação:** usar algoritmo próprio para senhas com salt e custo adaptativo; migrar/verificar hashes com segurança e remover senha realista do seed.
- **Validação:** dois hashes da mesma senha variam pelo salt, a verificação correta funciona e banco/log/resposta não contêm senha em claro.

### F-004 - [HIGH] Operações administrativas sem autenticação ou autorização

- **Localização:** `src/AppManager.js:80`
- **Categoria:** Segurança
- **Evidência:** relatório financeiro e exclusão em `src/AppManager.js:131` são registrados diretamente no Express sem middleware de identidade ou papel.
- **Impacto:** cliente anônimo pode consultar dados financeiros e nomes de alunos ou excluir usuários.
- **Recomendação:** aplicar autenticação verificável e autorização administrativa comum às duas routes, mantendo respostas de erro definidas como novo contrato de segurança.
- **Validação:** chamadas anônimas e de usuário comum são negadas; administrador autenticado acessa; identidade adulterada é rejeitada.

### F-005 - [HIGH] Checkout multi-etapas não é atômico

- **Localização:** `src/AppManager.js:50`
- **Categoria:** Confiabilidade
- **Evidência:** matrícula, pagamento e auditoria são inseridos sequencialmente sem `BEGIN`, `COMMIT` ou `ROLLBACK`; usuário novo é criado antes dessas etapas em `src/AppManager.js:69`.
- **Impacto:** falha intermediária deixa usuário ou matrícula órfãos e estado financeiro divergente.
- **Recomendação:** delimitar uma transação no Service de checkout e reverter todas as escritas diante de qualquer erro, incluindo auditoria conforme a política definida.
- **Validação:** induzir falha em cada escrita e comprovar que nenhuma alteração parcial permanece.

### F-006 - [HIGH] God Class mistura protocolo, domínios, regras e persistência

- **Localização:** `src/AppManager.js:4`
- **Categoria:** Arquitetura
- **Evidência:** `AppManager` abre banco, cria schema/seed, registra três routes, valida request, processa pagamento, executa SQL e formata responses.
- **Impacto:** mudanças independentes em checkout, relatórios, usuários ou infraestrutura atingem a mesma classe e exigem testes integrados amplos.
- **Recomendação:** adotar as camadas principais `routes/`, `controllers/` e `models/`, subdivididas por domínio; usar Services/Repositories somente para checkout transacional e consultas/exclusões complexas.
- **Validação:** teste arquitetural impede SQL em routes/controllers e dependência de HTTP em models/repositories; cada route delega ao controller do próprio domínio.

### F-007 - [HIGH] Banco e estado global concreto dificultam substituição e isolamento

- **Localização:** `src/AppManager.js:7`
- **Categoria:** Arquitetura
- **Evidência:** a classe instancia diretamente `sqlite3.Database`; `globalCache` mutável é singleton de módulo em `src/utils.js:9`.
- **Impacto:** testes e casos de uso ficam presos ao banco concreto e compartilham estado entre requests, com risco de vazamento e comportamento não determinístico.
- **Recomendação:** criar banco/cache na composição da aplicação e injetá-los nos componentes que precisam; usar ciclo de vida explícito e cache com contrato mínimo apenas se houver necessidade real.
- **Validação:** duas instâncias da aplicação usam bancos/caches isolados e Services podem ser testados com dependências controladas.

### F-008 - [MEDIUM] Relatório executa consultas N+1 aninhadas

- **Localização:** `src/AppManager.js:89`
- **Categoria:** Desempenho
- **Evidência:** para cada curso busca matrículas e, para cada matrícula, consulta usuário e pagamento nas linhas 92, 104 e 106.
- **Impacto:** o número de consultas cresce com cursos e matrículas, aumentando latência e carga do banco.
- **Recomendação:** encapsular consulta agregada parametrizada no Repository de relatórios, com `JOIN` e agregação ou conjunto pequeno e previsível de consultas.
- **Validação:** teste com múltiplos cursos/matrículas preserva o schema da resposta e mede quantidade constante ou limitada de consultas.

### F-009 - [MEDIUM] Validação de entrada é incompleta e inconsistente

- **Localização:** `src/AppManager.js:29`
- **Categoria:** Confiabilidade
- **Evidência:** o handler acessa `req.body` diretamente, não valida `pwd`, tipos, formato/tamanho de email/cartão ou inteiro positivo em `c_id`; senha ausente recebe default silencioso em `src/AppManager.js:68`.
- **Impacto:** entradas inválidas podem gerar exceções, credenciais fracas ou dados incoerentes, com respostas divergentes.
- **Recomendação:** validar o payload no limite HTTP com schema único, preservando campos externos e caracterizando previamente status/mensagens existentes.
- **Validação:** matriz cobre body ausente, tipos errados, limites, campos ausentes e valores malformados sem produzir `500` inesperado.

### F-010 - [MEDIUM] Erros assíncronos são ignorados ou classificados incorretamente

- **Localização:** `src/AppManager.js:37`
- **Categoria:** Confiabilidade
- **Evidência:** erro SQL e curso ausente viram o mesmo `404`; callbacks do relatório não verificam erros nas linhas 92, 104 e 106; auditoria ignora `err` em `src/AppManager.js:57`; delete ignora `err` em `src/AppManager.js:133` e sempre responde sucesso.
- **Impacto:** falhas internas podem causar exceção, resposta enganosa, request pendente ou confirmação de operação não realizada.
- **Recomendação:** propagar erros ao Controller e centralizar o mapeamento HTTP/log, distinguindo ausência de recurso de falha de infraestrutura.
- **Validação:** falhas injetadas em cada operação retornam erro consistente uma única vez, sem sucesso falso nem detalhe interno.

### F-011 - [MEDIUM] Exclusão viola integridade referencial

- **Localização:** `src/AppManager.js:12`
- **Categoria:** Confiabilidade
- **Evidência:** schema não declara foreign keys entre usuários, matrículas e pagamentos; o endpoint remove apenas `users` em `src/AppManager.js:133` e admite que deixa registros relacionados.
- **Impacto:** matrículas e pagamentos órfãos corrompem relatórios e histórico operacional.
- **Recomendação:** definir política de exclusão, constraints/FKs e operação transacional no domínio de usuários; decidir entre restrição, cascade ou anonimização conforme requisitos.
- **Validação:** excluir usuário com relações cumpre a política escolhida e `PRAGMA foreign_key_check` não encontra violações.

### F-012 - [MEDIUM] Configuração e ciclo de vida estão fixos no código

- **Localização:** `src/utils.js:1`
- **Categoria:** Manutenibilidade
- **Evidência:** credenciais e porta são constantes; banco `:memory:` é fixado em `src/AppManager.js:7`; `src/app.js:12` inicia o listener ao importar e não expõe encerramento.
- **Impacto:** deploy, teste isolado, readiness e desligamento gracioso ficam difíceis; importações causam efeito colateral.
- **Recomendação:** carregar ambiente validado, criar `createApp` sem listener e separar `start`, expondo encerramento do servidor e banco.
- **Validação:** aplicação inicia em porta efêmera/configurável, pode ser importada sem ouvir socket e encerra recursos previsivelmente.

### F-013 - [MEDIUM] Camadas MVC e limites dos três domínios são inexistentes

- **Localização:** `src/AppManager.js:25`
- **Categoria:** Arquitetura
- **Evidência:** `setupRoutes` contém checkout, relatório e gestão de usuários no mesmo método, sem `models/`, `routes/` ou `controllers/`.
- **Impacto:** dependências entre capacidades ficam implícitas e alterações de ritmos diferentes compartilham o mesmo arquivo.
- **Recomendação:** criar subpastas correspondentes `checkout`, `reports` e `users` dentro das camadas MVC utilizadas; cursos permanecem como dependência do checkout enquanto não houver fluxo autônomo de catálogo.
- **Validação:** árvore e teste arquitetural confirmam propriedade por domínio e ausência de imports entre Controllers.

### F-014 - [LOW] Nomes abreviados e import morto reduzem clareza

- **Localização:** `src/AppManager.js:29`
- **Categoria:** Manutenibilidade
- **Evidência:** variáveis `u`, `e`, `p`, `cid`, `cc`, `c` e `enr` ocultam significado; `totalRevenue` é importado em `src/AppManager.js:2` mas não usado.
- **Impacto:** leitura e revisão ficam mais lentas e o import sugere estado financeiro inexistente.
- **Recomendação:** usar nomes internos descritivos, preservando os campos externos, e remover import/export sem consumidor.
- **Validação:** análise estática não aponta import não usado e testes de contrato mantêm os nomes do JSON.

### F-015 - [LOW] Logs ad hoc e cache sem consumidor

- **Localização:** `src/utils.js:12`
- **Categoria:** Manutenibilidade
- **Evidência:** `logAndCache` usa `console.log`, muta `globalCache` e não há leitura desse cache; o boot também usa `console.log` em `src/app.js:13`.
- **Impacto:** há estado e ruído operacional sem benefício observável, níveis ou contexto estruturado.
- **Recomendação:** remover cache se não houver requisito; substituir logs por logger estruturado sem dados sensíveis e com níveis.
- **Validação:** busca não encontra `console.log` operacional nem escrita em cache sem consumidor; logs úteis possuem nível e contexto seguro.

## Avaliação arquitetural

- **Perfil MVC:** MVC separado por domínios dentro de cada camada, acrescido de Services/Repositories apenas onde agregam transação, consulta ou isolamento. Checkout, relatórios e gestão de usuários possuem fluxos, regras e motivos de mudança próprios.
- **Organização atual:** monólito sem camadas. `src/app.js` compõe minimamente o servidor, mas `AppManager` concentra toda a aplicação.
- **Mapa de domínios alvo:** checkout → `routes/checkout`, `controllers/checkout`, `models/checkout`, `services/checkout`, `repositories/checkout`; relatórios → `routes/reports`, `controllers/reports`, `models/reports` se houver política de saída, `services/reports` para agregação e `repositories/reports`; usuários → `routes/users`, `controllers/users`, `models/users`, com Service/Repository para senha e exclusão íntegra. Conexão, configuração, erros e logger técnicos podem ficar em `shared`.
- **Dependências entre domínios:** checkout usa usuários e cursos como dados participantes de sua transação; a integração deve ocorrer por Services/funções públicas, nunca importando Controllers. Relatórios leem dados de checkout/usuários por Repository de leitura próprio. Gestão de usuários deve aplicar uma política explícita às dependências de matrícula/pagamento.
- **SOLID:** SRP e DIP são violados por `AppManager` e dependências concretas. Não há hierarquias ou interfaces que evidenciem LSP/ISP; portanto não há achado desses princípios. Não há variação real suficiente para justificar estratégias OCP neste momento.
- **Responsabilidades MVC:** routes executam regra, SQL e formatação; não existem Controllers, Models ou Repositories. A direção alvo será `Route -> Controller -> Service -> Model/Repository`, admitindo `Controller -> Model/Repository` somente em CRUD simples.
- **Arquitetura-alvo:** MVC separado por domínios em cada camada, sem pasta `modules/` e sem interfaces/camadas de simples repasse.

## Plano de validação E2E

- **Fontes de contrato:** `api.http`, `README.md` e routes de `src/AppManager.js`; divergências e comportamentos não documentados serão registrados como caracterização.
- **Executor:** `node:test` e cliente HTTP nativo, evitando dependência nova; a aplicação deverá ser iniciada em processo/porta isolada ou por factory depois da aprovação.
- **Ambiente:** execução nativa isolada é suficiente para SQLite em memória. Docker Compose não agrega dependência externa neste projeto; poderá ser usado apenas se o ambiente exigir reprodutibilidade adicional.
- **Dependências:** banco SQLite exclusivo por execução; stub/fake local para pagamento se a regra for extraída como integração. Nenhum serviço real ou credencial será utilizado.
- **Cenários invariantes:** checkout aprovado e recusado; curso ausente; payload inválido; usuário existente/novo; relatório e sua agregação; exclusão e recurso ausente; formatos, status e efeitos persistentes observáveis.
- **Caracterização:** ordem do array do relatório; respostas atuais diante de body ausente, erros SQL e exclusão inexistente; comportamento de `paid` para pagamento não `PAID`; repetição de checkout.
- **Reprodução de defeitos:** ausência de autorização administrativa, vazamento no log, senha insegura, rollback em falhas intermediárias, integridade da exclusão, N+1 e erros ignorados.
- **Comparação:** a mesma suíte e seed serão executados antes/depois; IDs e ordem não garantida serão normalizados. Correções de segurança usarão expectativas seguras já definidas, sem exigir preservação da vulnerabilidade.
- **Artefatos futuros:** `reports/e2e-baseline-ecommerce-api-legacy.md` e `reports/e2e-after-ecommerce-api-legacy.md`.

## Escopo da refatoração

1. F-001, F-002, F-003 e F-004: retirar segredos/dados sensíveis, adotar hashing adequado e proteger operações administrativas.
2. F-005, F-007, F-011 e F-012: explicitar composição/ciclo de vida, transações, dependências e integridade.
3. F-006 e F-013: distribuir checkout, relatórios e usuários pelas camadas MVC principais, sem `modules/` ou camadas vazias.
4. F-008: substituir o fluxo N+1 por leitura agregada no Repository de relatórios.
5. F-009 e F-010: validar entrada e centralizar erros preservando contratos invariantes; alterações de segurança serão documentadas.
6. F-014 e F-015: limpar nomes/imports e observabilidade no código tocado pelos achados anteriores.

## Confirmação

Fase 2 concluída. Prosseguir com a refatoração (Fase 3)? [s/n]

**Status da aprovação:** aprovada explicitamente pelo usuário.

**Resposta registrada:** `sim`, recebida após a apresentação desta versão do relatório.

## Fase 3: resultado da refatoração

- **Arquitetura adotada:** MVC separado pelos domínios `checkout`, `reports` e `users`, com Services/Repositories que encapsulam transação, agregação e exclusão íntegra.
- **Achados tratados:** F-001 a F-015. A repetição da busca confirmou ausência dos segredos legados, do `AppManager`, do cache global, da transformação Base64 de senha e de SQL em Routes/Controllers/Models.
- **Segurança:** credenciais operacionais foram removidas; senhas usam `scrypt` com salt; logs descartam campos sensíveis; relatório e exclusão exigem `Authorization: Bearer <ADMIN_TOKEN>`.
- **Confiabilidade:** checkout usa rollback transacional; foreign keys e cascade preservam integridade; erros HTTP são centralizados; conexão e servidor possuem ciclo de vida explícito.
- **Desempenho:** o relatório usa uma consulta com `JOIN`, eliminando o N+1.
- **Validação estática/unitária/de integração:** `PASSOU` — `npm test`, 11 de 11 testes.
- **E2E antes:** `FALHOU` — 6 cenários passaram e a reprodução de vazamento em log falhou, conforme `reports/e2e-baseline-ecommerce-api-legacy.md`.
- **E2E depois:** `PASSOU` — 7 de 7 cenários, conforme `reports/e2e-after-ecommerce-api-legacy.md`.
- **Regressões de contrato:** nenhuma nos contratos invariantes. As respostas `401 Unauthorized` sem token nas operações administrativas são uma correção de segurança deliberada prevista por F-004.
- **Risco restante:** `npm ci` informou 13 vulnerabilidades no grafo legado de dependências (2 `low`, 3 `moderate`, 7 `high`, 1 `critical`). Atualizações potencialmente incompatíveis não foram aplicadas sem uma análise própria de dependências e contratos.
