# ♻️ Refatoração Arquitetural Automatizada com Codex Skills

Este repositório apresenta a implementação da skill `refactor-arch`, criada para analisar, auditar e refatorar aplicações backend para uma arquitetura MVC adaptada à tecnologia e ao domínio encontrados.

A skill foi validada em três projetos legados:

- `code-smells-project`: API de e-commerce em Python, Flask e SQLite;
- `ecommerce-api-legacy`: API de LMS e checkout em Node.js, Express e SQLite;
- `task-manager-api`: API de gerenciamento de tarefas em Python, Flask, Flask-SQLAlchemy e SQLite.

Nos três casos, a execução produziu uma análise da stack, um relatório de auditoria com evidências exatas, uma refatoração por camadas e domínios e uma comparação E2E antes/depois. Todos os contratos invariantes cobertos pelos testes permaneceram funcionando após as mudanças.

## 🧭 Sumário

- [Análise Manual](#análise-manual)
- [Construção da Skill](#construção-da-skill)
- [Resultados](#resultados)
- [Como Executar](#como-executar)
- [Relatórios](#relatórios)

## 🔍 Análise Manual

A análise manual foi feita antes da refatoração, considerando os arquivos originais do repositório. Os itens abaixo são uma seleção dos problemas de maior relevância; os relatórios de auditoria contêm a lista completa e as linhas exatas de cada ocorrência.

### 1️⃣ Projeto 1 — `code-smells-project`

O código original concentrava as rotas em `app.py`, regras e fluxo HTTP em `controllers.py`, persistência de todos os domínios em `models.py` e uma conexão global em `database.py`.

| Severidade | Problema identificado | Local original | Por que é relevante |
|---|---|---|---|
| CRITICAL | Console SQL público | `app.py:59` | O endpoint aceitava SQL fornecido pelo cliente sem autenticação, permitindo leitura, alteração ou exclusão arbitrária dos dados. |
| CRITICAL | SQL Injection | `models.py:48` e outras ocorrências | Entradas externas eram concatenadas diretamente às queries, inclusive nos fluxos de autenticação, catálogo e pedidos. |
| MEDIUM | Consultas N+1 em pedidos | `models.py:188` e `models.py:220` | Cada pedido disparava consultas adicionais para itens e produtos, fazendo a quantidade de queries crescer com o volume de dados. |
| MEDIUM | Validação inconsistente | `controllers.py:87`, `controllers.py:169` e `controllers.py:239` | JSON ausente, tipos incorretos e quantidades negativas podiam provocar erro 500 ou persistir dados inválidos. |
| LOW | Serialização duplicada | `models.py:188` e `models.py:220` | A mesma montagem de pedidos aparecia em mais de um fluxo, aumentando o risco de respostas divergentes. |
| LOW | Logs com `print` | `controllers.py:217` e `controllers.py:249` | Mensagens sem nível, contexto ou estrutura prejudicavam observabilidade e testes. |

Outros riscos importantes encontrados foram senhas em texto puro, exposição da `SECRET_KEY`, reset público do banco, debug habilitado, falta de atomicidade em pedidos e ausência de integridade referencial.

### 2️⃣ Projeto 2 — `ecommerce-api-legacy`

O projeto original tinha três arquivos-fonte. `AppManager.js` concentrava criação do banco, seed, rotas, validações, regras de checkout, SQL, relatórios e exclusão de usuários.

| Severidade | Problema identificado | Local original | Por que é relevante |
|---|---|---|---|
| CRITICAL | Segredos embutidos no código | `src/utils.js:2` | Credenciais e chave de pagamento versionadas poderiam ser extraídas do código ou do histórico do repositório. |
| CRITICAL | Cartão e chave de pagamento nos logs | `src/AppManager.js:45` | Dados financeiros e segredo operacional eram registrados integralmente, criando risco de vazamento e exposição regulatória. |
| HIGH | Operações administrativas sem autorização | `src/AppManager.js:80` e `src/AppManager.js:131` | Clientes anônimos podiam consultar o relatório financeiro e excluir usuários. |
| MEDIUM | Relatório com N+1 aninhado | `src/AppManager.js:89` | Para cada curso e matrícula eram feitas novas consultas de usuário e pagamento, degradando rapidamente o desempenho. |
| MEDIUM | Validação incompleta do checkout | `src/AppManager.js:29` | Tipos, senha, email, cartão e identificador do curso não eram validados de forma consistente. |
| LOW | Nomes abreviados e import morto | `src/AppManager.js:29` | Identificadores como `u`, `e`, `p` e `cid` escondiam o propósito das variáveis e dificultavam manutenção. |
| LOW | Cache sem consumidor e logs ad hoc | `src/utils.js:9` | O estado global era escrito, mas nunca lido; os logs não tinham níveis nem proteção sistemática de dados sensíveis. |

Também foram encontrados hashing reversível de senha, checkout sem transação, exclusão sem integridade referencial, erros assíncronos ignorados e forte acoplamento ao SQLite concreto.

### 3️⃣ Projeto 3 — `task-manager-api`

Embora já existissem Models, Routes e um Service, as Routes ainda concentravam acesso ao ORM, validação, regras, serialização e tratamento de erro. Controllers e limites claros entre os domínios não existiam.

| Severidade | Problema identificado | Local original | Por que é relevante |
|---|---|---|---|
| CRITICAL | Hash de senha exposto nas respostas | `models/user.py:28` | Listagem, detalhe, criação e login podiam devolver o campo de senha armazenado. |
| HIGH | Senhas em MD5 sem salt | `models/user.py:35` | MD5 é inadequado para armazenamento de senhas e permite ataques rápidos após o vazamento do banco. |
| MEDIUM | Consultas N+1 | `routes/task_routes.py:44` e `routes/report_routes.py:16` | As listagens carregavam relacionamentos individualmente, aumentando o número de queries conforme a base crescia. |
| MEDIUM | Validação e erros inconsistentes | `routes/task_routes.py:110` e `routes/user_routes.py:89` | Entradas inválidas podiam resultar em erro 500 HTML e transações não possuíam tratamento uniforme. |
| LOW | Regras e serialização duplicadas | `routes/task_routes.py:110` | Status, prioridade, datas e cálculo de atraso apareciam em Routes, Models e helpers sem proprietário claro. |
| LOW | Imports, helpers e dependências sem uso | `app.py:7` e `utils/helpers.py` | Código morto sugeria capacidades inexistentes e aumentava o custo de entendimento e atualização. |
| LOW | Logs com `print` e exceções cruas | `routes/task_routes.py:153` | Detalhes internos poderiam aparecer nos logs sem nível, correlação ou sanitização. |

Também foram identificados tokens previsíveis, ausência de autorização efetiva, segredo fixo, responsabilidades de vários domínios misturadas, configuração de desenvolvimento fixa e uso das APIs obsoletas `Query.get()` e `datetime.utcnow()`.

## 🛠️ Construção da Skill

### 🧰 Ferramenta e estrutura

A ferramenta escolhida foi o **OpenAI Codex**. Por isso, a skill foi instalada na convenção de repositório `.agents/skills/refactor-arch/` em cada projeto:

```text
<projeto>/
└── .agents/
    └── skills/
        └── refactor-arch/
            ├── SKILL.md
            ├── agents/
            │   └── openai.yaml
            └── references/
                ├── anti-pattern-catalog.md
                ├── architecture-principles.md
                ├── containerization-guidelines.md
                ├── contract-discovery.md
                ├── e2e-strategy.md
                ├── mvc-guidelines.md
                ├── project-analysis.md
                ├── refactoring-playbook.md
                └── report-template.md
```

As três cópias possuem o mesmo conteúdo. A [documentação oficial de Skills do Codex](https://developers.openai.com/codex/skills) define `SKILL.md` como obrigatório, permite referências auxiliares e informa que skills locais de repositório são descobertas em `.agents/skills`.

### 🔄 Fluxo em três fases

O `SKILL.md` executa um fluxo sequencial e controlado:

1. **Fase 1 — Análise:** detecta linguagem, runtime, framework, banco, domínio, arquitetura, contratos, testes e arquivos-fonte analisados.
2. **Fase 2 — Auditoria:** cruza evidências reais com o catálogo de anti-patterns, classifica severidades, informa arquivo e linha, define arquitetura-alvo e salva o relatório.
3. **Gate humano:** a skill encerra a execução e exige uma nova resposta explícita do usuário antes de modificar a aplicação.
4. **Fase 3 — Refatoração:** cria a linha de base E2E, reorganiza o projeto, corrige os achados aprovados e executa a mesma validação após as mudanças.

A aprovação antecipada ou genérica não é aceita. Cada projeto exige sua própria confirmação, registrada no relatório correspondente.

### 🛡️ Isolamento e consolidação dos relatórios

Durante cada execução, a skill trata o diretório do projeto atual como sua raiz e grava os artefatos em `reports/` no mesmo nível de `app.py` ou `package.json`. Ela não navega para diretórios pais nem cria arquivos fora do projeto analisado. Essa decisão reduz o risco de a skill manipular conteúdo fora do escopo autorizado e mantém cada auditoria autocontida.

Para atender ao formato final do desafio sem ampliar o escopo da skill, depois das três execuções os relatórios de auditoria locais foram apenas copiados para o `reports/` da raiz do repositório, com os nomes obrigatórios:

```text
reports/
├── audit-project-1.md
├── audit-project-2.md
└── audit-project-3.md
```

Os relatórios locais permanecem junto de seus respectivos projetos como evidência da execução isolada.

### 📚 Arquivos de referência

| Área | Arquivo | Responsabilidade |
|---|---|---|
| Análise de projeto | `project-analysis.md` | Heurísticas de detecção de stack, dependências, banco, entry point, testes e arquitetura. |
| Catálogo de anti-patterns | `anti-pattern-catalog.md` | 22 categorias distribuídas entre CRITICAL, HIGH, MEDIUM e LOW, incluindo APIs obsoletas. |
| Template de relatório | `report-template.md` | Formato da Fase 1, resumo por severidade, achados, plano E2E, confirmação e resultado final. |
| Guidelines MVC | `mvc-guidelines.md` | Responsabilidades e dependências permitidas entre Models, Views/Routes, Controllers, Services e Repositories. |
| Playbook | `refactoring-playbook.md` | 16 transformações com exemplos antes/depois. |
| Princípios arquiteturais | `architecture-principles.md` | Perfis MVC, separação por domínios, direção das dependências e avaliação SOLID. |
| Descoberta de contratos | `contract-discovery.md` | Hierarquia de evidências e inventário dos comportamentos que devem ser preservados. |
| Estratégia E2E | `e2e-strategy.md` | Linha de base, isolamento, reprodução de defeitos e comparação antes/depois. |
| Containerização | `containerization-guidelines.md` | Critérios para escolher Docker Compose ou execução nativa isolada. |

### 🚨 Anti-patterns cobertos

O catálogo inclui, entre outros:

- injeção e execução arbitrária;
- segredos e dados sensíveis expostos;
- autenticação ou criptografia insegura;
- God Class/God Method;
- ausência de atomicidade;
- estado global mutável;
- violações de SRP, OCP, LSP, ISP e DIP;
- regras de negócio em Routes/Controllers inadequados;
- consultas N+1;
- validação ausente ou inconsistente;
- tratamento de erros disperso;
- exclusão sem integridade referencial;
- configuração acoplada ao código;
- APIs obsoletas;
- duplicação, valores mágicos, código morto e logs impróprios.

O playbook transforma esses achados em ações concretas: parametrização de SQL, extração de configuração, password hashing, Controllers finos, transações, eliminação de N+1, validação e erros centralizados, application factory, Services/Repositories seletivos e organização de domínios dentro das camadas MVC.

### 🌐 Como a independência de tecnologia foi garantida

A skill não procura apenas nomes de arquivos específicos nem assume Flask ou Express. Ela:

- detecta a stack por manifestos, imports, pontos de entrada e lockfiles;
- adapta a terminologia de View para Routes em APIs backend;
- identifica responsabilidades pelo comportamento do código, não somente pela pasta atual;
- preserva contratos a partir de testes, documentação e declarações de rotas;
- usa sinais conceituais, como query dentro de loop, entrada concatenada em SQL ou regra presa ao handler HTTP;
- permite execução E2E nativa ou por Docker Compose conforme as dependências do projeto;
- cria Services e Repositories somente quando existe responsabilidade real, evitando camadas vazias.

O mesmo conteúdo da skill analisou duas aplicações Flask com níveis diferentes de organização e uma aplicação Express baseada em callbacks.

### 🧩 Desafios encontrados

- **Contratos inseguros:** comportamentos como exposição de senha e endpoints administrativos públicos não deveriam ser preservados. A solução foi separar invariantes de reproduções de defeitos e definir expectativas seguras antes da refatoração.
- **Projeto parcialmente organizado:** no Task Manager, simplesmente criar novas pastas não seria suficiente. A skill moveu regras e persistência para proprietários claros e adicionou testes de fronteiras arquiteturais.
- **Callbacks e transação no Node.js:** o driver SQLite original usava callbacks. Foi criado um adaptador assíncrono com transação explícita e rollback testável.
- **Isolamento E2E:** como os projetos usam SQLite e não exigem serviços externos, a execução nativa com banco temporário foi mais simples e reproduzível que adicionar Docker Compose artificialmente.
- **Permissão de socket:** uma primeira validação Node falhou com `EPERM` em ambiente restrito. Com permissão de rede local, a mesma suíte passou 11 de 11 testes sem mudança de código.

## 📊 Resultados

### 🧾 Resumo das auditorias

| Projeto | Stack detectada | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|---|---:|---:|---:|---:|---:|
| `code-smells-project` | Python 3.12.3, Flask 3.1.1, SQLite | 4 | 7 | 7 | 3 | **21** |
| `ecommerce-api-legacy` | Node.js 24.12.0, Express 4.22.1, SQLite | 2 | 5 | 6 | 2 | **15** |
| `task-manager-api` | Python 3.12.3, Flask 3.0.0, Flask-SQLAlchemy 3.1.1 | 1 | 4 | 8 | 3 | **16** |

Todos os relatórios superam o mínimo de cinco findings, possuem ao menos um CRITICAL ou HIGH, estão ordenados por severidade e registram arquivo e linha das evidências.

### 🔁 Comparação antes/depois

#### 1️⃣ Projeto 1

Antes:

```text
code-smells-project/
├── app.py             # rotas, configuração e endpoints administrativos
├── controllers.py     # todos os fluxos e regras
├── models.py          # todos os domínios e queries
└── database.py        # conexão global, schema e seed
```

Depois:

```text
code-smells-project/
├── app.py             # application factory e composição
├── models/{catalogo,pedidos,relatorios,usuarios}/
├── routes/{catalogo,operacional,pedidos,relatorios,usuarios}/
├── controllers/{catalogo,operacional,pedidos,relatorios,usuarios}/
├── services/{pedidos,relatorios,usuarios}/
├── repositories/{operacional,pedidos,relatorios}/
├── shared/{config,database,errors}.py
└── tests/{unit,integration,e2e,architecture}/
```

Principais resultados: remoção do console SQL e reset público, queries parametrizadas, senhas com hash, conexão por contexto, pedido transacional, restauração idempotente de estoque, eliminação de N+1 e erros JSON centralizados.

#### 2️⃣ Projeto 2

Antes:

```text
ecommerce-api-legacy/src/
├── app.js
├── AppManager.js      # banco, seed, rotas, regras, SQL e respostas
└── utils.js           # segredos, cache global e criptografia insegura
```

Depois:

```text
ecommerce-api-legacy/src/
├── app.js             # createApp, composição e lifecycle
├── models/{checkout,users}/
├── routes/{checkout,reports,users}/
├── controllers/{checkout,reports,users}/
├── services/{checkout,reports,users}/
├── repositories/{checkout,reports,users}/
└── shared/{auth,database,errors,config,logger}/
```

Principais resultados: remoção de segredos, `scrypt` com salt, logs sanitizados, autorização administrativa, checkout atômico, foreign keys/cascade, relatório sem N+1 e ciclo de vida explícito do banco e servidor.

#### 3️⃣ Projeto 3

Antes:

```text
task-manager-api/
├── app.py
├── models/{task,user,category}.py
├── routes/{task_routes,user_routes,report_routes}.py
├── services/notification_service.py
└── utils/helpers.py
```

Depois:

```text
task-manager-api/
├── app.py             # application factory e composição
├── models/{tasks,users,categories}/
├── routes/{tasks,users,categories,reports}/
├── controllers/{tasks,users,categories,reports}/
├── services/{tasks,users,reports}/
├── repositories/{tasks,users,categories,reports}/
├── shared/{auth,config,database,errors,time}.py
└── tests/{unit,integration,e2e,architecture}/
```

Principais resultados: remoção de hashes das respostas, password hashing adaptativo com migração de MD5 legado, tokens assinados, autorização por papel, validação centralizada, consultas agregadas e substituição de `Query.get()` e `datetime.utcnow()`.

### ✅ Checklist de validação

| Fase | Critério | Projeto 1 | Projeto 2 | Projeto 3 |
|---|---|:---:|:---:|:---:|
| Análise | Linguagem detectada corretamente | ✅ | ✅ | ✅ |
| Análise | Framework detectado corretamente | ✅ | ✅ | ✅ |
| Análise | Domínio descrito corretamente | ✅ | ✅ | ✅ |
| Análise | Arquivos-fonte contados com critério explícito | ✅ | ✅ | ✅ |
| Auditoria | Relatório segue o template | ✅ | ✅ | ✅ |
| Auditoria | Findings possuem arquivo e linha | ✅ | ✅ | ✅ |
| Auditoria | Ordem CRITICAL → LOW | ✅ | ✅ | ✅ |
| Auditoria | Pelo menos cinco findings | ✅ | ✅ | ✅ |
| Auditoria | API obsoleta verificada quando aplicável | ✅ | ✅ | ✅ |
| Auditoria | Pausa e aprovação antes da Fase 3 | ✅ | ✅ | ✅ |
| Refatoração | Estrutura baseada em MVC | ✅ | ✅ | ✅ |
| Refatoração | Configuração sem segredo hardcoded | ✅ | ✅ | ✅ |
| Refatoração | Models abstraem dados e regras próprias | ✅ | ✅ | ✅ |
| Refatoração | Views/Routes separadas | ✅ | ✅ | ✅ |
| Refatoração | Controllers concentram o fluxo | ✅ | ✅ | ✅ |
| Refatoração | Erros centralizados | ✅ | ✅ | ✅ |
| Refatoração | Entry point claro | ✅ | ✅ | ✅ |
| Refatoração | Aplicação inicia sem erros | ✅ | ✅ | ✅ |
| Refatoração | Contratos originais invariantes respondem | ✅ | ✅ | ✅ |

### 🧪 Logs de validação

Projeto 1:

```text
Ran 30 tests in 4.157s
OK

16 E2E + 5 arquitetura + 4 integração + 5 unitários
```

Projeto 2:

```text
tests 11
pass 11
fail 0

E2E após refatoração: PASSOU=7; FALHOU=0; NÃO EXECUTADO=0
```

Projeto 3:

```text
Ran 18 tests in 1.058s
OK

E2E: 30 de 30 cenários em PASSOU
23 contratos invariantes preservados + 7 defeitos corrigidos
```

### 🌉 Comportamento entre stacks

No projeto Flask monolítico, a skill precisou criar toda a separação arquitetural. No Express, adaptou o fluxo assíncrono e a persistência por callbacks para transações testáveis. No Task Manager, preservou a estrutura já útil e corrigiu limites de responsabilidade, segurança e APIs obsoletas sem impor uma reconstrução desnecessária.

Isso demonstra que as regras são baseadas em responsabilidades, contratos e sinais de código, e não em uma linguagem ou framework específico.

## 🚀 Como Executar

### 📋 Pré-requisitos

- Git;
- OpenAI Codex CLI ou extensão do Codex instalada e autenticada;
- Python 3.12 e `pip` para os projetos Flask;
- Node.js 24 e npm para o projeto Express.

O Codex identifica skills locais em `.agents/skills`. Dentro do Codex CLI ou da extensão, use `/skills` para listar as skills ou mencione explicitamente `$refactor-arch` no prompt.

### ⚙️ Executar a skill

Entre em cada projeto e inicie o Codex:

```bash
cd code-smells-project
codex
```

No prompt do Codex:

```text
$refactor-arch analise e audite este projeto
```

Ao final da Fase 2, revise o relatório e responda `s` ou `sim` para autorizar a Fase 3. Repita o processo de forma independente nos outros projetos:

```bash
cd ../ecommerce-api-legacy
codex

cd ../task-manager-api
codex
```

Se a skill não aparecer imediatamente após uma alteração, reinicie o Codex e use `/skills` para confirmar a descoberta.

### 🐍 Instalar e validar o Projeto 1

```bash
cd code-smells-project
python -m venv venv
venv/bin/pip install -r requirements.txt
venv/bin/python -m unittest discover -v
venv/bin/python -m unittest discover -v -s tests/e2e -p 'test_*.py'
venv/bin/python app.py
```

A aplicação inicia em `http://127.0.0.1:5000`. Em produção, `SECRET_KEY` deve ser fornecida pelo ambiente.

### 🟢 Instalar e validar o Projeto 2

```bash
cd ecommerce-api-legacy
npm install
npm test
npm run test:e2e
ADMIN_TOKEN=troque-este-token npm start
```

A aplicação inicia em `http://localhost:3000`. O relatório financeiro e a exclusão de usuários exigem `Authorization: Bearer <ADMIN_TOKEN>`.

### 🐍 Instalar e validar o Projeto 3

```bash
cd task-manager-api
python -m venv venv
venv/bin/pip install -r requirements.txt
venv/bin/python seed.py
venv/bin/python -m unittest discover -s tests -p 'test*.py' -v
venv/bin/python tests/e2e/run_contracts.py --stage after
venv/bin/python app.py
```

A aplicação inicia em `http://localhost:5000`. Obtenha um token em `POST /login` e envie `Authorization: Bearer <token>` aos endpoints protegidos.

## 📄 Relatórios

| Projeto | Auditoria consolidada | Auditoria local | Linha de base E2E | E2E após refatoração |
|---|---|---|---|---|
| Projeto 1 | [`audit-project-1.md`](reports/audit-project-1.md) | [`audit-code-smells-project.md`](code-smells-project/reports/audit-code-smells-project.md) | [`e2e-baseline-code-smells-project.md`](code-smells-project/reports/e2e-baseline-code-smells-project.md) | [`e2e-after-code-smells-project.md`](code-smells-project/reports/e2e-after-code-smells-project.md) |
| Projeto 2 | [`audit-project-2.md`](reports/audit-project-2.md) | [`audit-ecommerce-api-legacy.md`](ecommerce-api-legacy/reports/audit-ecommerce-api-legacy.md) | [`e2e-baseline-ecommerce-api-legacy.md`](ecommerce-api-legacy/reports/e2e-baseline-ecommerce-api-legacy.md) | [`e2e-after-ecommerce-api-legacy.md`](ecommerce-api-legacy/reports/e2e-after-ecommerce-api-legacy.md) |
| Projeto 3 | [`audit-project-3.md`](reports/audit-project-3.md) | [`audit-task-manager-api.md`](task-manager-api/reports/audit-task-manager-api.md) | [`e2e-baseline-task-manager-api.md`](task-manager-api/reports/e2e-baseline-task-manager-api.md) | [`e2e-after-task-manager-api.md`](task-manager-api/reports/e2e-after-task-manager-api.md) |

Cada relatório de auditoria registra a análise da stack, os findings, a arquitetura-alvo, o plano E2E, a confirmação humana e o resultado da refatoração. As versões consolidadas são cópias dos relatórios locais, sem alteração de conteúdo.
