# Relatório de Auditoria de Arquitetura

## Projeto

- **Nome:** `code-smells-project`
- **Stack:** Python 3.12.3, Flask 3.1.1, Flask-CORS 5.0.1 e SQLite via `sqlite3`
- **Domínio:** API de e-commerce com catálogo, usuários/autenticação, pedidos/estoque e relatórios de vendas
- **Escopo:** `app.py`, `controllers.py`, `models.py`, `database.py`, `requirements.txt` e `README.md`; foram excluídos `.git/`, `.agents/`, `.codex/`, `venv/`, dependências, caches, artefatos gerados e bancos
- **Fontes analisadas:** 4 arquivos Python, totalizando 780 linhas físicas (`wc -l`, incluindo linhas em branco); manifesto e documentação também foram lidos, mas não contados como fonte
- **Linha de base:** não executada durante a auditoria, para não criar nem popular `loja.db`; não foram encontrados testes automatizados
- **Infraestrutura:** não há Dockerfile, Docker Compose, CI, healthcheck de container, migrations ou seeds separados; schema e seed são executados de forma implícita por `database.py:14` no primeiro acesso ao banco
- **Alterações preexistentes:** a aplicação estava sem diferenças Git nos seis arquivos rastreados analisados; `.agents/` e `../.vscode/` já apareciam como não rastreados

## Fase 1: análise do projeto

```text
================================
FASE 1: ANÁLISE DO PROJETO
================================
Projeto:        code-smells-project
Linguagem:      Python 3.12.3
Framework:      Flask 3.1.1
Dependências:   Flask 3.1.1; Flask-CORS 5.0.1
Banco de dados: SQLite via sqlite3 e SQL direto
Domínio:        API de e-commerce
Domínios MVC:   catálogo; usuários/autenticação; pedidos/estoque; relatórios de vendas
Arquitetura:    MVC parcial, monolítica por arquivos, com domínios misturados
Perfil MVC:     separado por domínios, com Services/Repositories seletivos
Contratos:      README.md e declarações de rotas/handlers; sem OpenAPI, collection ou testes
Execução E2E:   nativa e isolada proposta; SQLite temporário; Compose ausente
Arquivos-fonte: 4 arquivos Python; excluídos dependências e artefatos gerados
Linhas-fonte:   780 linhas físicas
Ponto de entrada: app.py
Testes:         não encontrado
Inicialização:  pip install -r requirements.txt && python app.py
================================
```

### Capacidades coesas e distribuição atual

| Capacidade | Routes/Views | Controllers | Services | Models/Repositories | Dados e dependências |
|---|---|---|---|---|---|
| Catálogo | `app.py:11` | `controllers.py:5`, `controllers.py:111` | ausente | `models.py:4`, `models.py:285` | tabela `produtos`; é consumida por pedidos |
| Usuários e autenticação | `app.py:18` | `controllers.py:128`, `controllers.py:167` | ausente | `models.py:72`, `models.py:105` | tabela `usuarios`; pedidos recebem `usuario_id`, mas não confirmam sua existência |
| Pedidos e estoque | `app.py:23` | `controllers.py:188`, `controllers.py:237` | ausente | `models.py:133`, `models.py:171`, `models.py:275` | tabelas `pedidos` e `itens_pedido`; depende de usuários e catálogo e altera estoque |
| Relatórios de vendas | `app.py:28` | `controllers.py:257` | ausente | `models.py:235` | agrega dados de pedidos e aplica regra de desconto |
| Operação técnica | `app.py:30`, `app.py:32`, `app.py:47`, `app.py:59` | `controllers.py:264` e handlers no próprio `app.py` | ausente | acesso direto por `get_db()` | health, descoberta, reset e console SQL; não constitui domínio de negócio |

As capacidades não estão isoladas nas camadas: `controllers.py` e `models.py` acumulam todas elas. Pedidos necessitam de Service por coordenarem validação, cálculo, transação, estoque e notificações. Pedidos e relatórios justificam Repository pelas consultas e transações complexas; CRUD simples pode continuar em Models sem camada de repasse.

### Inventário de contratos HTTP

As 19 operações abaixo foram inferidas das declarações de rota e dos handlers. Não existe especificação OpenAPI, collection ou teste para funcionar como fonte superior. Nenhuma rota exige autenticação ou autorização.

| Método e caminho | Entrada principal | Resposta observada no código | Efeito persistente |
|---|---|---|---|
| `GET /` | nenhuma | `200`, objeto com `mensagem`, `versao` e `endpoints` | nenhum |
| `GET /produtos` | nenhuma | `200`, `{dados: [...], sucesso: true}` | inicialização implícita do banco no primeiro acesso |
| `GET /produtos/busca` | query `q`, `categoria`, `preco_min`, `preco_max` | `200`, `{dados, total, sucesso}`; conversão inválida pode produzir `500` | inicialização implícita do banco |
| `GET /produtos/<int:id>` | `id` no caminho | `200` com produto ou `404` | inicialização implícita do banco |
| `POST /produtos` | JSON com `nome`, `preco`, `estoque`; `descricao` e `categoria` opcionais | `201` com `dados.id`; `400` para parte das validações | insere produto |
| `PUT /produtos/<int:id>` | mesmo formato de criação | `200`, `400` ou `404` | atualiza produto |
| `DELETE /produtos/<int:id>` | `id` no caminho | `200` ou `404` | exclui produto |
| `GET /usuarios` | nenhuma | `200`, `{dados: [...], sucesso: true}`, atualmente incluindo `senha` | inicialização implícita do banco |
| `GET /usuarios/<int:id>` | `id` no caminho | `200` com usuário, atualmente incluindo `senha`, ou `404` | inicialização implícita do banco |
| `POST /usuarios` | JSON com `nome`, `email`, `senha` | `201` com `dados.id` ou `400` | insere usuário |
| `POST /login` | JSON com `email`, `senha` | `200` com usuário, `400` ou `401`; não emite token/sessão | consulta usuário |
| `POST /pedidos` | JSON com `usuario_id` e lista `itens[{produto_id, quantidade}]` | `201` com `pedido_id` e `total`, ou `400` | insere pedido/itens e reduz estoque |
| `GET /pedidos` | nenhuma | `200`, `{dados: [...], sucesso: true}` | inicialização implícita do banco |
| `GET /pedidos/usuario/<int:usuario_id>` | `usuario_id` no caminho | `200`, inclusive lista vazia para usuário inexistente | inicialização implícita do banco |
| `PUT /pedidos/<int:pedido_id>/status` | JSON com `status` | `200` ou `400`; atualmente retorna `200` para pedido inexistente | atualiza status quando o ID existe |
| `GET /relatorios/vendas` | nenhuma | `200` com totais, desconto e ticket médio | inicialização implícita do banco |
| `GET /health` | nenhuma | `200` com estado, contagens e configuração; `500` em falha | cria schema e seed no primeiro acesso |
| `POST /admin/reset-db` | nenhuma | `200` | exclui todos os dados das quatro tabelas |
| `POST /admin/query` | JSON com campo `sql` | `200`, `400` ou `500`; retorna linhas para texto iniciado por `SELECT` | executa qualquer instrução recebida e confirma não-`SELECT` |

O comando documentado de instalação é `pip install -r requirements.txt`; o de inicialização é `python app.py`. Não há comando de teste. A aplicação escuta `http://localhost:5000` segundo o README, embora o servidor esteja configurado em `0.0.0.0:5000`.

## Resumo da auditoria

| Severidade | Quantidade |
|---|---:|
| CRITICAL | 4 |
| HIGH | 7 |
| MEDIUM | 7 |
| LOW | 3 |
| **Total** | **21** |

## Achados

### F-001 - [CRITICAL] Console SQL público permite leitura e alteração arbitrárias

- **Localização:** `app.py:59`; execução em `app.py:69`
- **Categoria:** Segurança
- **Evidência:** `POST /admin/query` recebe o campo externo `sql`, entrega o texto integral a `cursor.execute()` e confirma qualquer comando que não comece com `SELECT`. Não existe autenticação ou allowlist.
- **Impacto:** um cliente remoto pode ler, alterar ou excluir todo o banco e consultar dados sensíveis; erros internos também são devolvidos ao cliente.
- **Recomendação:** remover o endpoint do runtime público. Se houver necessidade operacional comprovada, substituí-lo por operações administrativas específicas, autenticadas, autorizadas e auditadas, sem aceitar SQL do cliente.
- **Validação:** em banco temporário, comprovar que usuários anônimos e autenticados não conseguem executar SQL arbitrário e que as operações administrativas permitidas seguem autorização explícita.

### F-002 - [CRITICAL] Entradas externas são interpoladas diretamente em SQL

- **Localização:** `models.py:48`; ocorrências mecânicas adicionais em `models.py:58`, `models.py:110`, `models.py:127`, `models.py:140`, `models.py:149`, `models.py:158`, `models.py:164`, `models.py:291` e `models.py:293`
- **Categoria:** Segurança
- **Evidência:** valores oriundos de JSON ou query string, como nome, descrição, email, senha, identificadores dos itens, quantidade, termo e categoria, são concatenados ao SQL. As ocorrências foram agrupadas porque possuem a mesma causa e a mesma correção.
- **Impacto:** permite injeção SQL, desvio de autenticação, leitura indevida e corrupção de preço, estoque, pedidos e usuários. A limitação do SQLite a uma instrução por `execute()` não neutraliza manipulações dentro da própria instrução.
- **Recomendação:** usar placeholders `?` e parâmetros em todas as consultas; validar tipos, limites e identificadores antes da persistência; manter SQL em Model/Repository proprietário do domínio.
- **Validação:** executar payloads com aspas e operadores em cada fluxo vulnerável, verificando resultado literal, ausência de desvio de consulta e integridade do banco.

### F-003 - [CRITICAL] `SECRET_KEY` operacional está fixa e é exposta pelo health check

- **Localização:** `app.py:7`; exposição em `controllers.py:289`
- **Categoria:** Segurança
- **Evidência:** a mesma chave está gravada em código e retornada sem autenticação por `GET /health`.
- **Impacto:** consumidores podem obter o segredo usado pelo Flask para assinar dados, comprometendo qualquer recurso presente ou futuro baseado nessa chave; o segredo também permanece no histórico do repositório.
- **Recomendação:** remover o campo da resposta, carregar a chave do ambiente sem default sensível e rotacionar o valor antes de qualquer uso real.
- **Validação:** confirmar que `/health` não contém a chave e que a aplicação falha de modo explícito quando o segredo obrigatório não é fornecido no ambiente aplicável.

### F-004 - [CRITICAL] Senhas são armazenadas e devolvidas em texto puro

- **Localização:** `database.py:31`; seed em `database.py:76`; serializações em `models.py:83` e `models.py:99`
- **Categoria:** Segurança
- **Evidência:** a coluna `senha` recebe texto puro, o seed contém senhas recuperáveis e os endpoints públicos `GET /usuarios` e `GET /usuarios/<int:id>` incluem esse campo nas respostas.
- **Impacto:** qualquer acesso à API ou ao arquivo SQLite expõe credenciais reutilizáveis e permite tomada de contas em outros sistemas.
- **Recomendação:** remover `senha` de todas as projeções e respostas, aplicar password hashing adequado com salt por usuário e comparar pelo verificador da biblioteca; preparar migração segura para dados existentes.
- **Validação:** garantir que respostas e logs nunca contenham `senha`, que o banco armazene apenas hashes não reversíveis e que login correto/incorreto mantenha os status públicos esperados.

### F-005 - [HIGH] Reset destrutivo está disponível sem autorização

- **Localização:** `app.py:47`; primeira exclusão em `app.py:51`
- **Categoria:** Segurança
- **Evidência:** `POST /admin/reset-db` apaga itens, pedidos, produtos e usuários e não possui autenticação, autorização ou restrição de ambiente.
- **Impacto:** qualquer cliente pode apagar integralmente os dados da loja.
- **Recomendação:** retirar a operação da API pública; manter reset apenas em utilitário de testes isolado ou protegê-lo com autenticação administrativa real, autorização e bloqueio explícito fora de teste.
- **Validação:** comprovar que uma chamada anônima não altera dados e que o comando de reset de teste só atua no banco temporário criado pela suíte.

### F-006 - [HIGH] Servidor de desenvolvimento e depurador ficam expostos em todas as interfaces

- **Localização:** `app.py:8`; inicialização em `app.py:88`
- **Categoria:** Segurança
- **Evidência:** `DEBUG` é fixado como verdadeiro e `app.run(host="0.0.0.0", ..., debug=True)` publica o servidor de desenvolvimento.
- **Impacto:** aumenta a exposição de detalhes internos e, quando o depurador interativo fica alcançável, pode permitir execução de código; o servidor de desenvolvimento também não é apropriado para carga de produção.
- **Recomendação:** obter o modo de execução do ambiente, manter debug desabilitado por padrão e documentar um servidor WSGI apropriado para produção sem alterar o comando de desenvolvimento sem decisão explícita.
- **Validação:** iniciar com configuração de produção e confirmar debug desabilitado, respostas sem página de depuração e bind/servidor conforme a configuração escolhida.

### F-007 - [HIGH] Uma conexão SQLite global mutável é compartilhada entre requests

- **Localização:** `database.py:4`; criação em `database.py:10`
- **Categoria:** Confiabilidade
- **Evidência:** `db_connection` é singleton global e `check_same_thread=False` desliga a proteção do driver sem adicionar sincronização ou ciclo de vida por request.
- **Impacto:** requests concorrentes compartilham cursor transacional implícito, podendo confirmar ou reverter trabalho alheio, produzir corrida e vazar estado entre testes.
- **Recomendação:** usar conexão por contexto/request, fechá-la no teardown do Flask e injetar factory/conexão nas unidades de persistência; manter a transação pertencente a um caso de uso.
- **Validação:** executar pedidos concorrentes e testes isolados, verificando que cada request possui transação própria e que conexões são encerradas.

### F-008 - [HIGH] Criação de pedido não delimita rollback nem unidade atômica explícita

- **Localização:** `models.py:148`; gravações subsequentes em `models.py:158` e `models.py:164`; único commit em `models.py:168`
- **Categoria:** Confiabilidade
- **Evidência:** o fluxo insere pedido e itens e altera estoque em laços, mas não usa contexto transacional nem executa rollback ao falhar. Com a conexão global, trabalho parcial não confirmado pode ser confirmado por chamada posterior.
- **Impacto:** pedido, itens e estoque podem divergir após erro no meio do fluxo, concorrência ou entrada malformada.
- **Recomendação:** mover o caso de uso para Service de pedidos, abrir uma transação única, validar tudo antes da escrita e executar rollback em qualquer exceção; as operações SQL devem ficar no Model/Repository de pedidos.
- **Validação:** provocar falha após cada etapa e comprovar que pedido, itens e estoque permanecem no estado anterior.

### F-009 - [HIGH] Cancelamento anuncia reposição, mas apenas altera o status

- **Localização:** `controllers.py:249`; persistência em `models.py:280`
- **Categoria:** Confiabilidade
- **Evidência:** ao receber `cancelado`, o código imprime que devolverá o estoque, mas a única instrução persistente atualiza `pedidos.status`. O fluxo também aceita qualquer transição entre os cinco valores e não verifica linhas afetadas.
- **Impacto:** cancelamentos mantêm estoque reduzido, transições inválidas podem ocorrer e IDs inexistentes recebem resposta de sucesso, comprometendo disponibilidade e relatórios.
- **Recomendação:** definir uma política explícita de transições e reposição idempotente no Service de pedidos, executada na mesma transação, com detecção de pedido ausente.
- **Validação:** cobrir cancelamento, cancelamento repetido, transições inválidas e ID ausente, verificando status HTTP e estoque pela API.

### F-010 - [HIGH] Módulos centrais concentram múltiplos domínios e responsabilidades

- **Localização:** `controllers.py:5`; outros domínios começam em `controllers.py:128`, `controllers.py:188`, `controllers.py:257` e `controllers.py:264`; equivalentes em `models.py:4`, `models.py:72`, `models.py:133` e `models.py:235`
- **Categoria:** Arquitetura
- **Evidência:** dois módulos concentram catálogo, usuários/autenticação, pedidos/estoque, relatórios e operação, além de validação, regra, SQL, serialização e notificações.
- **Impacto:** há muitos motivos independentes de mudança, alto acoplamento e ampla superfície de regressão; testes de um domínio precisam carregar dependências dos demais.
- **Recomendação:** manter as camadas principais `routes/`, `controllers/` e `models/`, subdivididas por `catalogo`, `usuarios`, `pedidos` e `relatorios`; adicionar `services/` e `repositories/` apenas nos domínios com orquestração ou persistência complexa.
- **Validação:** adicionar testes de arquitetura para impedir SQL em Routes/Controllers, imports de Controllers entre domínios e arquivos multiárea nas camadas.

### F-011 - [HIGH] Fluxo HTTP depende diretamente da implementação global do banco

- **Localização:** `controllers.py:3`; uso direto em `controllers.py:266`; import concreto em `models.py:1`
- **Categoria:** Arquitetura
- **Evidência:** Controllers e todas as funções de persistência obtêm o singleton concreto por `get_db()`, sem factory/contexto substituível. O health check executa SQL diretamente no Controller.
- **Impacto:** testes necessitam do SQLite real e do estado global, responsabilidades MVC vazam e a troca de conexão ou isolamento transacional exige editar consumidores.
- **Recomendação:** criar a conexão na composição da aplicação, usar contexto do Flask e fornecer a dependência a Models/Repositories; mover consultas de health para componente técnico de persistência sem criar interface vazia.
- **Validação:** testar Controller/Service com dependência substituta e executar suíte paralela sem compartilhar banco.

### F-012 - [MEDIUM] Listagens de pedidos executam consultas N+1 duplicadas

- **Localização:** `models.py:188`; consulta adicional por item em `models.py:192`; repetição em `models.py:220` e `models.py:224`
- **Categoria:** Desempenho
- **Evidência:** cada pedido dispara uma consulta de itens e cada item dispara outra consulta de produto, nos dois métodos de listagem.
- **Impacto:** a quantidade de queries e a latência crescem proporcionalmente ao número de pedidos e itens.
- **Recomendação:** usar consulta com `JOIN` ou carga agregada no Repository de pedidos e compartilhar a montagem do resultado sem mudar o schema JSON.
- **Validação:** contar queries para conjuntos pequenos e grandes e confirmar quantidade constante ou limitada, preservando os campos e valores da resposta.

### F-013 - [MEDIUM] Validação de JSON, tipos e regras é inconsistente

- **Localização:** `controllers.py:169`; ocorrências independentes em `controllers.py:239`, `controllers.py:118`, `controllers.py:87` e `models.py:140`
- **Categoria:** Confiabilidade
- **Evidência:** login e atualização de status chamam `.get()` sem confirmar que o body é objeto; busca converte números sem erro de domínio; atualização de produto não repete a validação de categoria da criação; pedido indexa campos internos e não impede quantidade zero, negativa ou não numérica.
- **Impacto:** entradas inválidas geram `500`, dados fora das regras são persistidos e quantidade negativa pode elevar estoque e produzir total negativo.
- **Recomendação:** centralizar schemas/validadores nos limites, preservar mensagens/status já contratuais e adicionar regras de quantidade positiva, tipos numéricos, usuário/produto existentes e categoria consistente.
- **Validação:** matriz de JSON ausente, `null`, lista, campos ausentes, tipos errados, limites e quantidades não positivas, esperando respostas 4xx determinísticas e nenhuma escrita.

### F-014 - [MEDIUM] Schema não aplica integridade referencial

- **Localização:** `database.py:39`; referências sem constraint em `database.py:48` e `database.py:49`; exclusão em `models.py:68`
- **Categoria:** Confiabilidade
- **Evidência:** `pedidos.usuario_id`, `itens_pedido.pedido_id` e `itens_pedido.produto_id` não possuem `FOREIGN KEY`; a exclusão de produto não verifica itens já associados.
- **Impacto:** pedidos e itens órfãos podem ser criados ou preservados, degradando listagens, relatórios e auditoria histórica.
- **Recomendação:** definir FKs e política explícita de exclusão/retenção, habilitar enforcement do SQLite por conexão e aplicar migração reversível após decisão sobre dados existentes.
- **Validação:** tentar criar referências inexistentes e excluir registros referenciados, comprovando a política escolhida sem corromper dados.

### F-015 - [MEDIUM] Tratamento de erros é repetido e expõe detalhes internos

- **Localização:** `controllers.py:10`; repetido nos demais handlers e em `app.py:77`
- **Categoria:** Segurança
- **Evidência:** blocos amplos `except Exception` retornam `str(e)` diretamente ao cliente, misturando erro de domínio, entrada e infraestrutura.
- **Impacto:** detalhes de SQL e implementação podem vazar; falhas de cliente viram `500`; diagnóstico e rollback são inconsistentes.
- **Recomendação:** centralizar mapeamento de exceções do Flask, criar erros de domínio específicos e registrar contexto técnico sem dados sensíveis, retornando mensagens públicas estáveis.
- **Validação:** provocar falhas de validação e banco, confirmando status apropriados, resposta sem detalhes internos e log correlacionável.

### F-016 - [MEDIUM] Configuração de execução e CORS estão acoplados ao código

- **Localização:** `app.py:9`; porta e bind em `app.py:88`; caminho do banco em `database.py:5`
- **Categoria:** Arquitetura
- **Evidência:** `CORS(app)` libera origens sem política explícita, enquanto host, porta e caminho SQLite são valores fixos.
- **Impacto:** ambientes não podem isolar banco e porta de forma segura, e navegadores de qualquer origem podem chamar a API, agravando os endpoints sem autenticação.
- **Recomendação:** carregar configuração de ambiente com defaults não sensíveis, restringir origens conforme o ambiente e permitir arquivo SQLite/porta temporários para testes.
- **Validação:** subir duas instâncias isoladas com configurações distintas e testar origens permitidas e rejeitadas.

### F-017 - [MEDIUM] Orquestração e notificações de pedidos permanecem no Controller

- **Localização:** `controllers.py:208`; transições e notificações em `controllers.py:247`
- **Categoria:** Arquitetura
- **Evidência:** após criar ou atualizar pedido, o Controller decide e simula email, SMS, push e eventos de expedição/estoque por `print`, acoplando regra e efeitos ao transporte HTTP.
- **Impacto:** os casos de uso não podem ser reutilizados fora do HTTP, falhas de integração não participam da consistência e testes precisam exercitar o handler inteiro.
- **Recomendação:** mover a orquestração para Service de pedidos, com portas injetáveis apenas para integrações reais; o Controller deve traduzir request/response.
- **Validação:** testar regras e falhas de notificação no Service sem request Flask, além do contrato HTTP invariável.

### F-018 - [MEDIUM] Não existe suíte automatizada para os contratos e riscos atuais

- **Localização:** `README.md:5`
- **Categoria:** Manutenibilidade
- **Evidência:** a documentação oferece apenas instalação e inicialização; o inventário não encontrou arquivos de teste, configuração de runner ou comando de teste.
- **Impacto:** mudanças em 19 operações HTTP, persistência e correções de segurança não possuem proteção contra regressão observável.
- **Recomendação:** criar na Fase 3 uma suíte E2E de caracterização antes de alterar a aplicação e testes unitários/de integração para transação, validação, autenticação e consultas.
- **Validação:** executar o comando documentado da suíte em estado limpo e registrar resultados `PASSOU`, `FALHOU` ou `NÃO EXECUTADO` nos relatórios antes/depois.

### F-019 - [LOW] Serialização e montagem de pedidos estão duplicadas

- **Localização:** `models.py:12`; serialização equivalente em `models.py:304`; montagem duplicada em `models.py:177` e `models.py:209`
- **Categoria:** Manutenibilidade
- **Evidência:** mapas de produto e loops de pedido/itens são copiados em funções distintas.
- **Impacto:** inclusão ou correção de campos pode ocorrer em apenas um caminho e gerar respostas divergentes.
- **Recomendação:** extrair mapeadores internos coesos ou consolidar consultas, sem criar camada sem responsabilidade.
- **Validação:** comparar schemas de produtos e pedidos nos endpoints correspondentes após a extração.

### F-020 - [LOW] Logs são feitos com `print` e mensagens ad hoc

- **Localização:** `controllers.py:8`; exemplos adicionais em `controllers.py:161`, `controllers.py:179`, `controllers.py:208` e `app.py:56`
- **Categoria:** Manutenibilidade
- **Evidência:** sucessos, falhas, emails de usuário e ações críticas são enviados diretamente à saída padrão, sem nível, correlação ou estrutura.
- **Impacto:** observabilidade é inconsistente e informações pessoais podem aparecer em logs sem política.
- **Recomendação:** usar o logger do Flask/Python com níveis e campos seguros; não registrar senha, segredo nem corpo sensível.
- **Validação:** capturar logs de sucesso/erro e verificar nível, contexto e ausência de dados sensíveis.

### F-021 - [LOW] Import não utilizado cria sinalização falsa

- **Localização:** `models.py:2`
- **Categoria:** Manutenibilidade
- **Evidência:** `sqlite3` é importado, mas o módulo usa apenas a conexão obtida de `database.get_db`.
- **Impacto:** pequeno ruído de leitura e falsa indicação de responsabilidade sobre criação de conexões.
- **Recomendação:** remover o import após garantir que nenhum uso dinâmico dependa dele.
- **Validação:** executar análise estática e a suíte sem warnings de import não utilizado.

## Avaliação arquitetural

- **Perfil MVC:** MVC separado por domínios dentro de cada camada, com Services/Repositories seletivos. Há quatro capacidades com regras e ritmos próprios; pedidos possui transação e orquestração reais, e pedidos/relatórios possuem persistência complexa.
- **Organização atual:** híbrida e apenas parcialmente MVC. `app.py` registra rotas, mas também contém SQL e operações administrativas; `controllers.py` reúne transporte, validação, regra e notificações; `models.py` reúne regra e persistência de todos os domínios.
- **Mapa de domínios alvo:** `catalogo -> routes/catalogo, controllers/catalogo, models/catalogo`; `usuarios -> routes/usuarios, controllers/usuarios, models/usuarios, services/usuarios` para autenticação; `pedidos -> routes/pedidos, controllers/pedidos, models/pedidos, services/pedidos, repositories/pedidos`; `relatorios -> routes/relatorios, controllers/relatorios, repositories/relatorios`. Componentes técnicos de conexão, configuração e erros podem ficar em `shared`, sem regras de negócio.
- **Dependências entre domínios:** pedidos consulta usuários e catálogo e altera estoque; relatórios lê pedidos. Essas interações devem ocorrer por Services/funções públicas, nunca por import de Controller. A composição das dependências deve ocorrer na criação da aplicação.
- **SOLID:** SRP é violado pelos módulos multiárea e pelos fluxos que misturam HTTP, regras, SQL e notificações; DIP é violado pelo singleton concreto acessado diretamente. Não há hierarquia, subtipo ou interface suficiente para sustentar achados de LSP ou ISP. Também não há variação real repetida que justifique estratégia por OCP neste momento.
- **Responsabilidades MVC:** Routes devem apenas declarar entrada; Controllers devem traduzir e coordenar; regras/transações reutilizáveis devem ficar em Services; SQL deve ficar em Models/Repositories. Hoje SQL aparece em Routes e Controller, e regras/notificações aparecem em Controller.
- **APIs obsoletas:** nenhuma API suspeita ou aviso local foi encontrado nas versões declaradas. A auditoria não executou runtime/testes e, portanto, não afirma ausência absoluta de obsolescência.
- **Arquitetura-alvo:** MVC separado por domínios em cada camada, sem pasta `modules/`, com Service para autenticação e pedidos e Repository somente para transações/consultas complexas de pedidos e relatórios.

Estrutura proposta, sujeita ao gate:

```text
app.py
routes/
  catalogo/
  usuarios/
  pedidos/
  relatorios/
  operacional/
controllers/
  catalogo/
  usuarios/
  pedidos/
  relatorios/
  operacional/
models/
  catalogo/
  usuarios/
  pedidos/
services/
  usuarios/
  pedidos/
repositories/
  pedidos/
  relatorios/
shared/
  config.py
  database.py
  errors.py
tests/
  e2e/
  unit/
  integration/
```

## Plano de validação E2E

- **Fontes de contrato:** `README.md`, regras de rota de `app.py` e handlers de `controllers.py`; todas são inferências controladas por ausência de especificação/testes superiores.
- **Executor:** `unittest` da biblioteca padrão com `Flask.test_client()`, evitando dependência nova e exercitando o contrato WSGI completo. O mesmo conjunto de testes será usado antes e depois.
- **Ambiente:** execução nativa isolada é a menor solução adequada. Cada rodada usará diretório temporário, arquivo SQLite exclusivo e limpeza apenas dos recursos criados pelo teste. Docker Compose não agrega isolamento relevante ao SQLite atual; se a parametrização segura não puder ser obtida sem alterar a aplicação, a linha de base será interrompida e registrada como `NÃO EXECUTADO` para decisão do usuário.
- **Dependências:** SQLite temporário; não existem cache, fila ou integração externa real. Saídas simuladas de email/SMS/push serão capturadas ou substituídas sem chamada externa.
- **Prontidão:** inicializar pelo primeiro acesso controlado e validar `GET /health`; não reutilizar `loja.db` do diretório do usuário.
- **Cenários invariantes:** descoberta em `/`; CRUD e busca de produtos; criação/consulta/login de usuário; criação, consulta e status de pedido; relatório; health; status 400/401/404 documentados; schemas e efeitos persistentes observados pela API.
- **Caracterização:** registrar os comportamentos atuais de pedido inexistente, JSON malformado, quantidade não positiva, categoria divergente e inicialização implícita, sem obrigar a versão corrigida a preservar defeitos.
- **Reprodução de defeitos:** cobrir F-001 a F-009, F-012 a F-016, especialmente console SQL, reset anônimo, payloads de injeção, campos sensíveis, debug, isolamento de conexão, rollback, cancelamento/estoque, N+1 por contagem de queries, validação, órfãos, mensagens de erro e CORS.
- **Testes complementares:** unitários para transições, cálculo e validadores; integração para transação, FKs, consultas parametrizadas e quantidade de queries; arquitetura para direção `route/view -> controller -> service -> model/repository` e separação dos domínios.
- **Comando planejado:** `venv/bin/python -m unittest discover -s tests/e2e -p 'test_*.py'`.
- **Artefatos:** `reports/e2e-baseline-code-smells-project.md` e `reports/e2e-after-code-smells-project.md`, com cada cenário marcado como `PASSOU`, `FALHOU` ou `NÃO EXECUTADO`.

## Escopo da refatoração

1. **Segurança imediata (F-001 a F-006):** remover consoles destrutivos do runtime público, parametrizar SQL, retirar/rotacionar segredo, proteger senhas, introduzir autorização administrativa e separar configuração de desenvolvimento/produção.
2. **Consistência e dependências (F-007 a F-009, F-011):** trocar singleton por ciclo de vida por request, injetar persistência, tornar pedidos transacionais e implementar política idempotente de status/estoque.
3. **Arquitetura por domínio (F-010, F-017):** distribuir catálogo, usuários, pedidos e relatórios sob as camadas MVC principais; criar Services/Repositories somente nas áreas justificadas acima; não criar `modules/`.
4. **Persistência e limites (F-012 a F-016):** eliminar N+1, centralizar validação/erros, aplicar integridade referencial após plano de migração e externalizar configuração/CORS.
5. **Proteção e acabamento (F-018 a F-021):** registrar linha de base E2E antes da aplicação, adicionar testes focados, reduzir duplicação, estruturar logs e remover código morto.

Mudanças de schema, política de autenticação, comportamento de endpoints administrativos e respostas atualmente defeituosas serão tratadas como correções de vulnerabilidade/defeito, com expectativas definidas na linha de base. URLs, métodos, campos públicos legítimos e status não associados aos defeitos permanecerão invariantes. Qualquer migração irreversível ou quebra adicional exigirá autorização específica.

## Confirmação

Fase 2 concluída. Prosseguir com a refatoração (Fase 3)? [s/n]

**Status da aprovação:** aprovada explicitamente pelo usuário.

**Resposta recebida:** `s`
