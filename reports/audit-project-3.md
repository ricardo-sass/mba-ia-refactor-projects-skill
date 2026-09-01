# Relatório de Auditoria de Arquitetura

## Fase 1 — Análise do projeto

```text
================================
FASE 1: ANÁLISE DO PROJETO
================================
Projeto:        task-manager-api
Linguagem:      Python 3.12.3 (runtime do ambiente virtual local)
Framework:      Flask 3.0.0 + Flask-SQLAlchemy 3.1.1 / SQLAlchemy 2.0.52
Dependências:   Flask-Cors 4.0.0, marshmallow 3.20.1, requests 2.31.0 e python-dotenv 1.0.0
Banco de dados: SQLite, acessado por Flask-SQLAlchemy; URI sqlite:///tasks.db
Domínio:        gerenciamento de tarefas, usuários, categorias e relatórios
Domínios MVC:   tarefas, usuários/autenticação, categorias e relatórios; notificações são capacidade de apoio de tarefas
Arquitetura:    MVC parcial, com Models e Routes, sem Controllers; regras e persistência estão nos handlers HTTP
Perfil MVC:     separado por domínios, com Services/Repositories seletivos
Contratos:      README.md, decorators de rota, models e seed.py; não há OpenAPI, collection ou testes
Execução E2E:   nativa e isolada em cópia temporária, por usar SQLite; Compose não agrega isolamento necessário
Arquivos-fonte: 15 arquivos .py, excluídos venv, .agents, .codex, reports e artefatos gerados
Linhas-fonte:   1.158 linhas físicas nos 15 arquivos .py analisados
Ponto de entrada: app.py
Testes:         não encontrado
Inicialização:  pip install -r requirements.txt && python seed.py && python app.py
================================
```

### Stack e dependências

- A versão da linguagem foi verificada com `venv/bin/python --version`.
- As versões diretas são fixadas em `requirements.txt`; SQLAlchemy 2.0.52 foi verificado no ambiente instalado como dependência transitiva.
- `marshmallow`, `requests` e `python-dotenv` estão declarados, mas não possuem uso no código analisado.
- A aplicação expõe HTTP com Flask, habilita CORS globalmente e persiste em SQLite por meio de Flask-SQLAlchemy.

### Arquitetura atual e capacidades coesas

| Capacidade | Entradas atuais | Models/dados | Regras e efeitos | Dependências |
|---|---|---|---|---|
| Tarefas | `routes/task_routes.py`; parte de `routes/user_routes.py` | `models/task.py`, tabela `tasks` | CRUD, busca, status, prioridade, vencimento, tags e estatísticas | usuários e categorias por chaves estrangeiras; notificações ainda não conectadas |
| Usuários e autenticação | `routes/user_routes.py` | `models/user.py`, tabela `users` | CRUD, senha, login, papel, ativação e tarefas do usuário | tarefas para listagem e exclusão |
| Categorias | trecho de `routes/report_routes.py` iniciado em `routes/report_routes.py:157` | `models/category.py`, tabela `categories` | CRUD e contagem de tarefas | tarefas para contagem e associação |
| Relatórios | trecho de `routes/report_routes.py` iniciado em `routes/report_routes.py:12` | não possui Model próprio; consulta as três tabelas | resumo operacional e produtividade por usuário | tarefas, usuários e categorias |
| Notificações de tarefas | nenhuma Route conectada | lista em memória em `services/notification_service.py` | envio SMTP e registro de atribuição | SMTP concreto; usuários e tarefas recebidos como objetos |

As quatro primeiras capacidades têm linguagem, fluxos e motivos de mudança próprios. Categorias não devem permanecer dentro de uma Route de relatórios. Notificações não justificam um domínio MVC independente neste estado: são uma integração de apoio ao fluxo de tarefas e devem ficar no Service desse domínio, com cliente externo injetável.

### Contratos HTTP descobertos

A fonte de contrato é o código das Routes, cruzado com o `README.md` e o seed. Não há autenticação ou autorização efetivamente exigida por nenhuma operação. IDs e timestamps são dinâmicos; datas são serializadas com `str()`.

| Método e caminho | Entrada | Sucesso observado/inferido | Erros codificados e efeito |
|---|---|---|---|
| `GET /` | nenhuma | `200`, objeto com `message` e `version` | sem persistência |
| `GET /health` | nenhuma | `200`, `status` e `timestamp` | healthcheck HTTP; não verifica banco |
| `GET /tasks` | nenhuma | `200`, lista enriquecida com usuário, categoria e `overdue` | `500` JSON genérico; sem persistência |
| `GET /tasks/<task_id>` | path inteiro | `200`, Task e `overdue` | `404` quando ausente |
| `POST /tasks` | `title`, `description`, `status`, `priority`, `user_id`, `category_id`, `due_date`, `tags` | `201`, Task criada | `400`, `404` ou `500`; insere em `tasks` |
| `PUT /tasks/<task_id>` | atualização parcial dos mesmos campos | `200`, Task atualizada | `400`, `404` ou `500`; atualiza `tasks` |
| `DELETE /tasks/<task_id>` | path inteiro | `200`, mensagem | `404` ou `500`; exclui de `tasks` |
| `GET /tasks/search` | query `q`, `status`, `priority`, `user_id` | `200`, lista de Tasks | conversões inválidas não são tratadas; sem persistência |
| `GET /tasks/stats` | nenhuma | `200`, totais por status, atraso e taxa | sem persistência |
| `GET /users` | nenhuma | `200`, lista sem senha e com `task_count` | sem persistência |
| `GET /users/<user_id>` | path inteiro | `200`, usuário e respectivas Tasks | `404`; inclui indevidamente o campo `password` |
| `POST /users` | `name`, `email`, `password`, `role` | `201`, usuário | `400`, `409` ou `500`; insere em `users` e devolve indevidamente `password` |
| `PUT /users/<user_id>` | `name`, `email`, `password`, `role`, `active` | `200`, usuário | `400`, `404`, `409` ou `500`; atualiza `users` e devolve indevidamente `password` |
| `DELETE /users/<user_id>` | path inteiro | `200`, mensagem | `404` ou `500`; exclui Tasks do usuário e depois o usuário na mesma sessão |
| `GET /users/<user_id>/tasks` | path inteiro | `200`, lista resumida com `overdue` | `404`; sem persistência |
| `POST /login` | `email`, `password` | `200`, mensagem, usuário e token previsível | `400`, `401` ou `403`; devolve indevidamente `password` |
| `GET /reports/summary` | nenhuma | `200`, visão geral, status, prioridades, atrasos, atividade e produtividade | sem persistência |
| `GET /reports/user/<user_id>` | path inteiro | `200`, usuário e estatísticas | `404`; sem persistência |
| `GET /categories` | nenhuma | `200`, lista com `task_count` | sem persistência |
| `POST /categories` | `name`, `description`, `color` | `201`, categoria | `400` ou `500`; insere em `categories` |
| `PUT /categories/<cat_id>` | atualização parcial | `200`, categoria | `404` ou `500`; atualiza `categories` |
| `DELETE /categories/<cat_id>` | path inteiro | `200`, mensagem | `404` ou `500`; exclui de `categories` |

### Persistência, inicialização e infraestrutura

- `app.py:30` executa `db.create_all()` durante a importação do módulo.
- `seed.py` exclui e recria dados de exemplo em três grupos de commits; ele não é idempotente de forma atômica e modifica o banco, por isso não foi executado durante esta auditoria.
- Não foram encontrados migrations, Dockerfile, Docker Compose, CI, `.dockerignore`, testes, OpenAPI, arquivos `.http` ou collections.
- Existe `GET /health`, mas ele não verifica disponibilidade da persistência.
- O diretório `venv/` é uma dependência gerada e foi excluído da contagem de fonte, embora seu runtime e seus metadados tenham sido usados para confirmar versões.
- Nenhum teste nem servidor foi executado nas Fases 1 e 2. A linha de base comportamental está, portanto, **NÃO EXECUTADA** até a Fase 3 aprovada.

## Fase 2 — Auditoria

## Projeto

- **Nome:** task-manager-api
- **Stack:** Python 3.12.3, Flask 3.0.0, Flask-SQLAlchemy 3.1.1, SQLAlchemy 2.0.52 e SQLite
- **Escopo:** 15 arquivos Python, `README.md` e `requirements.txt`; excluídos `venv/`, `.agents/`, `.codex/`, `.git/`, bancos e artefatos gerados
- **Linha de base:** testes e inicialização não executados durante a auditoria; não existem testes automatizados no projeto

## Resumo

| Severidade | Quantidade |
|---|---:|
| CRITICAL | 1 |
| HIGH | 4 |
| MEDIUM | 8 |
| LOW | 3 |
| **Total** | **16** |

## Achados

### F-001 — [CRITICAL] Hash de senha exposto por contratos públicos

- **Localização:** `models/user.py:21`
- **Categoria:** Segurança
- **Evidência:** `User.to_dict()` inclui `password`. Esse serializer é usado por `GET /users/<user_id>` em `routes/user_routes.py:33`, pelas respostas de criação e atualização em `routes/user_routes.py:85` e `routes/user_routes.py:129`, e pelo login em `routes/user_routes.py:209`.
- **Impacto:** qualquer consumidor desses endpoints obtém hashes de senha. Como o hash também é rápido e sem salt, a exposição viabiliza quebra offline e comprometimento de contas.
- **Recomendação:** remover `password` de toda representação pública e criar serializers explícitos por contrato; nunca devolver hash, mesmo ao próprio usuário.
- **Validação:** testes E2E devem afirmar que `password` não existe em nenhuma resposta de usuário ou login e reproduzir a exposição na linha de base sem manter a vulnerabilidade como invariante.

### F-002 — [HIGH] Senhas armazenadas com MD5 sem salt e política mínima insuficiente

- **Localização:** `models/user.py:29`
- **Categoria:** Segurança
- **Evidência:** `set_password()` e `check_password()` usam MD5 direto; `routes/user_routes.py:64` aceita senha de quatro caracteres.
- **Impacto:** hashes vazados podem ser quebrados com baixo custo, inclusive os das contas criadas pelo seed.
- **Recomendação:** usar password hashing adaptativo do ecossistema, com salt e fator de custo, manter verificação compatível para migração gradual e elevar a política de senha sem invalidar dados silenciosamente.
- **Validação:** testes unitários devem confirmar salt distinto para senhas iguais, verificação válida/inválida e migração do formato legado; E2E deve preservar o fluxo de login autorizado.

### F-003 — [HIGH] Autenticação previsível e ausência de autorização efetiva

- **Localização:** `routes/user_routes.py:210`
- **Categoria:** Segurança
- **Evidência:** o login devolve um token formado por texto fixo e ID. Nenhuma Route valida esse token; operações mutáveis, como `POST /tasks` em `routes/task_routes.py:85`, ficam públicas, e `POST /users` aceita `role` fornecido pelo cliente em `routes/user_routes.py:52`.
- **Impacto:** qualquer cliente pode alterar dados sem identidade verificada; o token pode ser forjado e os papéis não protegem nenhuma operação.
- **Recomendação:** implementar autenticação verificável com expiração e segredo vindo do ambiente, aplicar autorização por operação e impedir autoatribuição de papéis privilegiados. A correção altera intencionalmente o comportamento inseguro de acesso anônimo.
- **Validação:** E2E deve cobrir login, token inválido/expirado, ausência de token, usuário inativo, papéis permitidos e negação de mutações não autorizadas.

### F-004 — [HIGH] Credenciais e segredos fixos no código

- **Localização:** `services/notification_service.py:10`
- **Categoria:** Segurança
- **Evidência:** o Service mantém uma senha SMTP literal e tenta autenticar em um host real; `app.py:13` também fixa o `SECRET_KEY`. Os valores não são reproduzidos neste relatório. A validade da credencial SMTP não foi testada.
- **Impacto:** se a credencial for operacional, o repositório permite uso indevido da conta; o segredo fixo do Flask permite falsificação de dados assinados quando sessões ou recursos equivalentes forem usados.
- **Recomendação:** revogar/rotacionar qualquer credencial operacional, carregar segredos obrigatórios do ambiente, falhar com mensagem segura quando ausentes e usar valores falsos exclusivos nos testes.
- **Validação:** varredura de segredos, teste de inicialização sem variável obrigatória e E2E com SMTP falso, sem rede externa.

### F-005 — [HIGH] Routes concentram transporte, regras, persistência e serialização

- **Localização:** `routes/task_routes.py:11`
- **Categoria:** Arquitetura
- **Evidência:** `routes/task_routes.py` tem 299 linhas e executa consultas, validação, regra de atraso, serialização, commits e logs. O padrão se repete em `routes/user_routes.py:10` (211 linhas) e `routes/report_routes.py:12` (223 linhas). Não existe camada Controllers.
- **Impacto:** viola SRP, aumenta o acoplamento ao Flask e ao ORM e exige banco/HTTP para testar regras simples; mudanças pequenas têm ampla superfície de regressão.
- **Recomendação:** manter Routes finas, criar Controllers por domínio para fluxo HTTP e Services apenas para regras/orquestrações reais; mover persistência complexa para Repositories.
- **Validação:** testes de arquitetura devem impedir SQL/`db.session` em Routes e testes unitários devem exercitar regras sem request nem banco real quando apropriado.

### F-006 — [MEDIUM] Relatórios e categorias compartilham a mesma Route sem limite de domínio

- **Localização:** `routes/report_routes.py:157`
- **Categoria:** Arquitetura
- **Evidência:** o arquivo iniciado como relatórios em `routes/report_routes.py:12` também implementa todo o CRUD de categorias a partir da linha 157.
- **Impacto:** categorias e relatórios mudam por motivos independentes, tornam propriedade e dependências implícitas e ampliam regressões cruzadas.
- **Recomendação:** manter as pastas principais `routes`, `controllers` e `models`, com subpastas correspondentes `categories` e `reports`; relatórios podem depender de APIs públicas/Repositories dos dados necessários, sem importar Controller de outro domínio.
- **Validação:** teste de arquitetura deve conferir os domínios correspondentes em cada camada e proibir importação entre Controllers.

### F-007 — [MEDIUM] Consultas N+1 em listagens e relatórios

- **Localização:** `routes/task_routes.py:42`
- **Categoria:** Desempenho
- **Evidência:** cada Task da listagem consulta usuário e categoria individualmente (`routes/task_routes.py:42` e `routes/task_routes.py:51`). Há repetição por usuário em `routes/report_routes.py:56`, por categoria em `routes/report_routes.py:163` e por usuário ao avaliar `len(u.tasks)` em `routes/user_routes.py:22`.
- **Impacto:** o número de consultas cresce linearmente com os registros e multiplica a latência e a carga do banco.
- **Recomendação:** usar eager loading/join nas listagens e agregações SQL agrupadas nos relatórios e contagens; encapsular consultas complexas em Repositories dos domínios proprietários.
- **Validação:** teste de integração deve limitar o número de consultas para conjuntos de tamanhos diferentes e confirmar o mesmo schema de resposta.

### F-008 — [MEDIUM] Validação de entrada é inconsistente e permite respostas 500 evitáveis

- **Localização:** `routes/task_routes.py:261`
- **Categoria:** Confiabilidade
- **Evidência:** `priority` e `user_id` são convertidos com `int()` sem tratamento. Outros handlers presumem tipos corretos após `request.get_json()`, como `routes/task_routes.py:87`, e `update_category()` usa o body em `routes/report_routes.py:196` sem validar se existe ou se é objeto.
- **Impacto:** query strings ou JSON sintaticamente válidos com tipos inesperados provocam exceções e respostas 500/HTML em vez do erro 400 JSON esperado no restante da API.
- **Recomendação:** validar entrada no limite HTTP com schemas coesos por domínio, preservando nomes de campos e mensagens/status já contratados quando não forem defeitos.
- **Validação:** E2E parametrizado com body ausente, array, string, números inválidos, datas inválidas e campos fora dos limites deve retornar JSON 400 sem persistir dados.

### F-009 — [MEDIUM] Tratamento de erro amplo, disperso e sem observabilidade consistente

- **Localização:** `routes/task_routes.py:62`
- **Categoria:** Confiabilidade
- **Evidência:** `except:` captura inclusive exceções de controle e converte causas distintas em um único 500. O padrão aparece também em `routes/report_routes.py:186` e `routes/user_routes.py:130`; outros blocos repetem rollback e formatação manual.
- **Impacto:** defeitos ficam ocultos, respostas divergem entre endpoints e o diagnóstico depende de `print`, com risco de rollback ou mapeamento incorreto em novas operações.
- **Recomendação:** capturar exceções específicas, centralizar o mapeamento HTTP e garantir rollback no limite transacional, com logs estruturados e sem dados sensíveis.
- **Validação:** testes de integração devem simular conflito e falha de persistência, verificar rollback, status/schema e registro seguro da causa.

### F-010 — [MEDIUM] NotificationService depende diretamente de SMTP concreto

- **Localização:** `services/notification_service.py:15`
- **Categoria:** Arquitetura
- **Evidência:** o próprio Service instancia `smtplib.SMTP`, autentica, envia e mantém estado em memória. Não há composição na inicialização nem uso do Service pelas Routes.
- **Impacto:** viola DIP, torna testes dependentes de rede e mistura integração, regra de notificação e armazenamento efêmero; falhas são reduzidas a `False` e ignoradas pelos métodos chamadores.
- **Recomendação:** injetar um cliente de e-mail na composição da aplicação, separar registro de notificação quando ele tiver uso real e remover a capacidade morta se ela continuar desconectada.
- **Validação:** teste unitário com cliente falso deve verificar conteúdo e falha; E2E deve bloquear qualquer conexão SMTP real.

### F-011 — [MEDIUM] Inicialização possui efeitos colaterais e configuração de desenvolvimento fixa

- **Localização:** `app.py:30`
- **Categoria:** Arquitetura
- **Evidência:** a instância Flask é global, `db.create_all()` executa na importação e `app.py:34` inicia em `debug=True`, host e porta fixos. Não existem factory, migrations ou configuração de teste.
- **Impacto:** importar a aplicação pode criar/alterar banco, o schema não possui evolução versionada, testes podem tocar estado local e uma execução exposta usa configuração de desenvolvimento.
- **Recomendação:** criar application factory configurável, retirar criação de schema da importação, introduzir migrations antes de evoluções de schema e parametrizar debug, URI, host e porta.
- **Validação:** importar a factory não deve criar arquivos; teste deve iniciar duas aplicações com bancos temporários independentes; execução não deve habilitar debug por padrão.

### F-012 — [MEDIUM] Query.get é legado na versão instalada do SQLAlchemy

- **Localização:** `routes/task_routes.py:67`
- **Categoria:** Obsolescência
- **Evidência:** a versão instalada é SQLAlchemy 2.0.52 e o projeto repete `Model.query.get()` em Routes de tarefas, usuários e relatórios. A [documentação oficial do SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/orm/queryguide/query.html#sqlalchemy.orm.Query.get) classifica `Query.get()` como legado e direciona para `Session.get()`.
- **Impacto:** mantém a persistência no estilo legado, gera avisos e aumenta o custo de futuras atualizações.
- **Recomendação:** substituir buscas por chave por `db.session.get(Model, id)` dentro de Models/Repositories, sem alterar semântica de identidade ou 404.
- **Validação:** testes de integração devem cobrir recurso existente/ausente e executar com avisos de depreciação tratados como erro.

### F-013 — [MEDIUM] datetime.utcnow está obsoleto no Python 3.12

- **Localização:** `models/task.py:15`
- **Categoria:** Obsolescência
- **Evidência:** o runtime é Python 3.12.3 e `datetime.utcnow()` aparece em Models, Routes, Service, utilitário e seed. A [documentação oficial do Python 3.12](https://docs.python.org/3.12/library/datetime.html#datetime.datetime.utcnow) o marca como obsoleto desde 3.12 e recomenda `datetime.now(UTC)`.
- **Impacto:** datas UTC sem timezone são ambíguas; uma troca ingênua pode ainda quebrar comparações entre registros antigos sem timezone e novos valores conscientes de timezone.
- **Recomendação:** definir uma política UTC única, adaptar persistência e serialização de modo compatível e migrar incrementalmente para valores conscientes de timezone, com decisão explícita antes de qualquer migração de dados.
- **Validação:** testes devem congelar o relógio, cobrir vencimento e limites de sete dias e comparar registros legados/novos sem `TypeError` nem alteração indevida do contrato textual.

### F-014 — [LOW] Regras e serialização estão duplicadas apesar de existirem helpers

- **Localização:** `routes/task_routes.py:110`
- **Categoria:** Manutenibilidade
- **Evidência:** status, prioridade, datas, tags e atraso são validados/calculados repetidamente nas Routes, em `models/task.py:38` e em `utils/helpers.py:57`; os helpers e constantes não são efetivamente usados.
- **Impacto:** correções podem produzir mensagens, limites ou resultados divergentes entre criação, atualização, listagem e relatórios.
- **Recomendação:** manter uma regra com proprietário claro no Model/Service do domínio e serializers explícitos por contrato; remover helpers duplicados em vez de criar abstrações genéricas.
- **Validação:** testes parametrizados devem aplicar a mesma matriz de status, prioridade, data e atraso a todos os fluxos pertinentes.

### F-015 — [LOW] Código, imports e dependências sem uso aumentam ruído

- **Localização:** `app.py:7`
- **Categoria:** Manutenibilidade
- **Evidência:** `sys`, `json` e `os` são importados sem uso; o padrão se repete em Routes e `utils/helpers.py`. `format_date` e `calculate_percentage` são importados em `routes/report_routes.py:7`, mas não chamados; `NotificationService` não é conectado; três dependências declaradas não aparecem no código.
- **Impacto:** o projeto sugere capacidades inexistentes, amplia manutenção de dependências e dificulta distinguir código ativo de rascunhos.
- **Recomendação:** remover imports, helpers e dependências comprovadamente mortos; conectar NotificationService somente se fizer parte do escopo funcional aprovado.
- **Validação:** análise estática sem imports não usados e execução completa dos testes após a remoção.

### F-016 — [LOW] Logs usam print e incluem detalhes crus de exceção

- **Localização:** `routes/task_routes.py:153`
- **Categoria:** Manutenibilidade
- **Evidência:** criação e atualização imprimem mensagens ad hoc; falhas de Task, User e SMTP incluem `str(e)` em `print`, como também ocorre em `routes/user_routes.py:89` e `services/notification_service.py:24`.
- **Impacto:** não há níveis, correlação nem formato consistente, e mensagens do driver ou da integração podem expor detalhes operacionais nos logs.
- **Recomendação:** usar o logger do Flask/Python com nível, contexto mínimo e sanitização; não registrar senha, token, body completo nem dados pessoais desnecessários.
- **Validação:** teste com captura de logs deve confirmar nível/contexto e ausência de dados sensíveis em falhas.

## Avaliação arquitetural

- **Perfil MVC:** `MVC separado por domínios`, pois tarefas, usuários/autenticação, categorias e relatórios possuem fluxos e ritmos de mudança próprios. Services/Repositories entram seletivamente para autenticação, validações/regras reutilizadas, SMTP e consultas agregadas/N+1.
- **Organização atual:** por camadas parciais; existem `models/`, `routes/` e um `services/`, mas não Controllers e nem subpastas de domínio. As Routes executam responsabilidades de todas as camadas.
- **Mapa de domínios alvo:**
  - tarefas → `models/tasks/`, `routes/tasks/`, `controllers/tasks/`, `services/tasks/` e `repositories/tasks/` apenas para busca/listagem complexa;
  - usuários/autenticação → `models/users/`, `routes/users/`, `controllers/users/` e `services/users/` para senha, autenticação e autorização;
  - categorias → `models/categories/`, `routes/categories/` e `controllers/categories/`; Repository somente se consultas deixarem de ser simples;
  - relatórios → `routes/reports/`, `controllers/reports/`, `services/reports/` e `repositories/reports/` para agregações; não requer Model artificial;
  - notificações → integração interna em `services/tasks/`, com adaptador SMTP técnico injetado; não será criada pasta `modules/`.
- **Dependências entre domínios:** tarefas referencia usuários e categorias; usuários consulta/exclui tarefas; relatórios lê os três domínios. A integração deve ocorrer por Services/funções públicas ou Repositories de leitura claramente definidos, nunca por importação de Controllers.
- **SOLID:** SRP e DIP estão violados pelos F-005, F-006 e F-010. Não há variação real que justifique estratégia para OCP, nem hierarquias/interfaces que evidenciem violações de LSP ou ISP; criar interfaces vazias não é recomendado.
- **Responsabilidades MVC:** Routes tratam request/response, regras, SQL, transação e serialização; Controllers estão ausentes; Models misturam persistência e alguns serializers/regras; o único Service mistura integração e estado.
- **Arquitetura-alvo:** direção principal `Route -> Controller -> Service -> Model/Repository`, permitindo `Controller -> Model` no CRUD simples de categorias quando Service seria mero repasse.

## Plano de validação E2E

- **Fontes de contrato:** decorators e handlers Flask, Models, `seed.py` e `README.md`.
- **Executor:** cliente HTTP da biblioteca padrão ou do ecossistema já instalado, executado contra processo Flask real; não adicionar runner apenas por convenção.
- **Ambiente:** execução nativa isolada. Antes da refatoração, copiar somente a aplicação para diretório temporário, usar o `venv/bin/python` existente, criar/seedear o SQLite dentro da cópia e publicar porta efêmera. Depois, reconstruir outra cópia limpa e executar exatamente a mesma suíte.
- **Dependências:** SQLite temporário; SMTP bloqueado e substituído por falso quando a capacidade for conectada. Não há cache, fila ou outro serviço externo detectado.
- **Readiness:** aguardar `GET /health` responder, registrando que o health atual não prova a saúde do banco; complementar com cenário de leitura.
- **Cenários invariantes:** raiz e health; CRUD e 404 de Tasks, Users e Categories; busca e filtros; estatísticas e relatórios; associação entre Task/User/Category; serialização, status e efeitos persistentes; exclusão de usuário e suas Tasks; login válido/inválido/inativo.
- **Entradas inválidas:** body ausente/não objeto, IDs ausentes, email, status, prioridade, data, tags, cor e query numérica inválidos; confirmar resposta JSON e ausência de escrita parcial.
- **Reprodução de defeitos:** F-001 a F-004 (segurança), F-007 (contagem de consultas via integração), F-008/F-009 (500 e rollback), F-012/F-013 (warnings e datas). Vulnerabilidades devem ser demonstradas antes e bloqueadas depois, não preservadas.
- **Caracterização que exige cuidado:** autenticação hoje não protege endpoints e as respostas de usuário incluem `password`; a correção desses comportamentos é intencional no escopo de segurança, preservando caminhos e campos não sensíveis. A transição de timestamps deve preservar o formato observável até decisão específica.
- **Artefatos:** `reports/e2e-baseline-task-manager-api.md` e `reports/e2e-after-task-manager-api.md`.
- **Estado atual:** **NÃO EXECUTADO**, pois a Fase 3 ainda não foi aprovada.

Docker Compose não é proposto como executor primário: a única dependência é SQLite, e uma cópia temporária com porta efêmera oferece isolamento reprodutível com menos infraestrutura. Um `compose.e2e.yml` só deverá ser criado após aprovação se a execução nativa se mostrar insuficiente.

## Escopo da refatoração

1. Criar a linha de base E2E isolada e interromper se ela não puder ser executada.
2. Tratar F-001 a F-004 primeiro: serializers seguros, password hashing, autenticação/autorização e configuração externa de segredos.
3. Tratar F-005 e F-006 ao distribuir os quatro domínios dentro das camadas principais `models/`, `routes/` e `controllers/`, sem `modules/`.
4. Tratar F-007 com consultas agregadas/eager loading e Repositories seletivos de tarefas/relatórios.
5. Tratar F-008 e F-009 com validação no limite, erros centralizados e transações explícitas.
6. Tratar F-010 e F-011 com composição de dependências, application factory, configuração por ambiente e migrations não destrutivas.
7. Tratar F-012 e F-013 preservando semântica de identidade, datas existentes e contrato textual.
8. Tratar F-014 a F-016 com remoção de duplicação/código morto e logging estruturado.
9. Executar a mesma suíte E2E em ambiente limpo, comparar contratos e registrar riscos restantes.

Não serão executadas migrações irreversíveis nem mudanças adicionais de contrato sem nova decisão explícita. Alterações preexistentes fora deste projeto permanecem fora do escopo.

## Confirmação

Fase 2 concluída. Prosseguir com a refatoração (Fase 3)? [s/n]

**Status da aprovação:** aprovada explicitamente pelo usuário.

**Resposta registrada:** `sim`, recebida em 25/08/2026 para esta versão do relatório.

## Resultado da Fase 3

- **Arquitetura adotada:** MVC separado por domínios, com Services e Repositories seletivos.
- **Linha de base:** `reports/e2e-baseline-task-manager-api.md` — 23 invariantes em PASSOU e 7 defeitos reproduzidos.
- **Após refatoração:** `reports/e2e-after-task-manager-api.md` — 30 de 30 cenários em PASSOU.
- **Validação adicional:** 18 testes unitários, integrados e arquiteturais em PASSOU; `pip check` e `git diff --check` em PASSOU.
- **Achados tratados:** F-001 a F-016; a compatibilidade com MD5 permanece apenas como leitura controlada para migração imediata, sem geração de novos hashes legados.
