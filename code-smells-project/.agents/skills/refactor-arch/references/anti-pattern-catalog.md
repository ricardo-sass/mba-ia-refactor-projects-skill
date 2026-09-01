# Catálogo De Anti-Patterns

Usar os sinais como ponto de partida e confirmar o fluxo completo antes de registrar um achado. Elevar ou reduzir a severidade quando a exposição real justificar e explicar a decisão.

## Sumário

- CRITICAL: execução arbitrária e exposição de segredos
- HIGH: autenticação, God Class, atomicidade, estado global, DIP e LSP
- MEDIUM: SRP, mistura de domínios, OCP, ISP, N+1, regras em rotas, validação, erros, integridade, configuração e APIs obsoletas
- LOW: duplicação, código morto e logs impróprios
- Critérios de severidade

## CRITICAL

### Injeção E Execução Arbitrária

Sinais: concatenação/interpolação de entrada em SQL, shell, template ou avaliador; endpoint que aceita SQL ou comandos; uso de `eval` em dados externos.

Impacto: leitura, alteração ou destruição de dados e possível execução remota. Recomendar parâmetros, allowlists e remoção de consoles administrativos inseguros.

### Segredos Ou Dados Sensíveis Expostos

Sinais: chaves, senhas ou tokens reais no código; health/debug retornando segredo; cartão ou senha em logs; serialização de hash de senha.

Impacto: comprometimento de contas e sistemas. Diferenciar credencial de exemplo inequívoca de segredo operacional, mas nunca permitir exposição em resposta ou log.

## HIGH

### Autenticação Ou Criptografia Insegura

Sinais: MD5/SHA simples para senha, Base64 como hash, senha em texto puro, token previsível/falso, endpoint administrativo sem autorização.

Impacto: tomada de conta ou acesso privilegiado. Recomendar biblioteca de password hashing e autenticação verificável.

### God Class Ou God Method

Sinais: módulo ou classe concentra roteamento, validação, regras, persistência, integrações e formatação; muitos motivos para mudar; callbacks profundamente aninhados.

Impacto: alto acoplamento, testes difíceis e regressão ampla. Separar por responsabilidade e domínio.

### Ausência De Atomicidade

Sinais: fluxo de negócio grava várias tabelas sem transação; retorna no meio sem rollback; pagamento e matrícula/pedido podem divergir.

Impacto: dados inconsistentes. Delimitar transação no caso de uso e reverter em qualquer falha.

### Estado Global Mutável Ou Conexão Compartilhada

Sinais: cache, contador ou conexão global alterada entre requests; `check_same_thread=False`; singleton com estado de request.

Impacto: corrida, vazamento entre requests e comportamento não determinístico. Usar ciclo de vida do framework e dependência explícita.

### Acoplamento A Implementações Concretas (DIP)

Sinais: Controller ou Service instancia diretamente banco, cliente HTTP ou integração difícil de substituir; seleção de implementação espalhada pelo fluxo; testes exigem rede ou banco real sem necessidade.

Impacto: regras ficam acopladas a detalhes externos e testes exigem infraestrutura desnecessária. Criar dependências na inicialização da aplicação e recebê-las por construtor, factory ou parâmetro quando isso reduzir o acoplamento.

### Quebra De Substituição (LSP)

Sinais: implementação de interface exige verificações por subtipo, recusa entradas aceitas pelo contrato, muda semântica de retorno ou lança exceções não previstas.

Impacto: consumidores não podem substituir implementações com segurança. Corrigir o contrato, dividir a abstração ou preferir composição.

## MEDIUM

### Responsabilidades Múltiplas (SRP)

Sinais: módulo muda por motivos independentes, como transporte, regra de negócio, persistência e integração; testes exigem dependências não relacionadas ao comportamento exercitado.

Impacto: mudanças pequenas possuem superfície ampla de regressão. Separar por motivo de mudança e manter coesão.

### Camadas MVC Sem Separação Por Domínio

Sinais: arquivos soltos em `controllers`, `services`, `models` ou `repositories` acumulam capacidades independentes sem subpastas de domínio; um Service ou Repository conhece áreas sem a mesma transação; um arquivo mistura regras de vários domínios; `shared` contém regras sem proprietário.

Impacto: limites de negócio ficam implícitos, dependências cruzadas crescem e a evolução de uma área afeta outras. Manter as pastas MVC principais e criar dentro de cada camada subpastas correspondentes aos domínios. Não registrar quando o projeto possuir uma única capacidade pequena ou quando a separação for apenas nominal.

### Rigidez Para Extensão (OCP)

Sinais: cada novo tipo, provedor ou política exige editar condicionais centrais repetidamente; branches representam estratégias intercambiáveis.

Impacto: extensão frequente altera código estável e aumenta regressões. Extrair estratégia ou política somente quando a variação for real.

### Interface Maior Que A Necessidade Do Consumidor (ISP)

Sinais: implementações possuem métodos vazios ou `NotImplemented`; consumidores recebem dependência extensa para usar uma única capacidade.

Impacto: acoplamento e mocks desnecessariamente grandes. Dividir interfaces pela necessidade de cada consumidor.

### Consultas N+1

Sinais: query dentro de loop de entidades; carga individual de relação por item; callbacks encadeados por registro.

Impacto: latência e carga crescem com os dados. Usar join, eager loading ou consulta agregada.

### Controller Ou Route Com Regra De Negócio

Sinais: cálculos, transições de estado, notificações, persistência e validação de domínio dentro do handler HTTP.

Impacto: regra acoplada ao transporte e difícil de testar. Mover orquestração para Controller/Service e manter a Route como camada de entrada.

### Validação Inconsistente Ou Ausente

Sinais: body assumido como objeto, conversão numérica sem tratamento, listas/status divergentes, validação duplicada, campos sem limites.

Impacto: erros 500, dados inválidos e comportamento divergente. Centralizar schema e mensagens preservando o contrato.

### Tratamento De Erro Disperso Ou Silencioso

Sinais: `except:` amplo, detalhes internos em resposta, erro ignorado em callback, respostas 200 após falha, rollback inconsistente.

Impacto: diagnóstico ruim e estado incorreto. Centralizar mapper de erros e log estruturado sem dados sensíveis.

### Exclusão Sem Integridade Referencial

Sinais: delete de pai sem cascade ou verificação; registros filhos órfãos; schema sem foreign keys.

Impacto: dados corrompidos. Definir FKs, cascade apropriado ou transação de exclusão explícita.

### Configuração Acoplada Ao Código

Sinais: debug, portas, caminhos, hosts ou credenciais fixos; ambiente de produção declarado no handler.

Impacto: deploy inseguro e pouca portabilidade. Carregar ambiente com defaults apenas para valores não sensíveis.

### API Obsoleta

Sinais: warning de runtime/teste; método marcado como deprecated na versão instalada; API removida na próxima major. Exemplos: `Model.query.get` em SQLAlchemy 2, `datetime.utcnow()` em runtimes que recomendam datas timezone-aware, APIs Node marcadas como obsoletas.

Impacto: warnings, incompatibilidade futura e semântica ambígua. Confirmar a versão e recomendar o substituto oficial; não classificar apenas por memória.

## LOW

### Duplicação E Valores Mágicos

Sinais: serialização/validação repetida, listas de status e limites copiados, números ou strings de domínio espalhados.

Impacto: alterações inconsistentes. Extrair constantes ou funções somente quando houver uso real repetido.

### Nomes, Imports E Código Morto

Sinais: nomes sem significado (`u`, `e`, `p`), imports/exports não usados, variável importada imutável esperando atualização, branches redundantes.

Impacto: leitura difícil e falsa sinalização. Remover ou renomear sem mudar o contrato externo.

### Logs Impróprios

Sinais: `print` ad hoc, mensagem sem contexto, logs de sucesso em biblioteca, ausência de níveis.

Impacto: observabilidade fraca. Usar logger do ecossistema e campos sem dados sensíveis.

## Severidade

- `CRITICAL`: exploração grave, perda/exposição de dados ou violação arquitetural total com impacto imediato.
- `HIGH`: segurança ou acoplamento forte que compromete manutenção, teste ou consistência.
- `MEDIUM`: problema relevante de confiabilidade, performance, validação ou separação.
- `LOW`: legibilidade e manutenção localizada sem risco operacional imediato.
