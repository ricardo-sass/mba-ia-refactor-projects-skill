# Diretrizes De Arquitetura MVC

Aplicar MVC tradicional como separação de responsabilidades, respeitando as convenções do framework.

## Model

Representar e validar dados e regras próximas ao estado. Encapsular persistência simples no Model quando essa for a convenção da tecnologia. Não receber request/response nem formatar respostas HTTP.

## View Ou Route

Declarar método/caminho, extrair entrada, chamar Controller e converter o resultado em resposta. Não executar query, transação ou regra de negócio substancial. Para APIs JSON, tratar serializers/presenters como View e routers/blueprints como entrada.

## Controller

Coordenar o fluxo da requisição, validação contextual e chamadas a Services, Models ou Repositories. Retornar resultado ou erro adequado para a View/Route. Evitar SQL, detalhes de integração e regras reutilizáveis.

## Service

Concentrar regras de negócio e orquestrações reutilizadas por controllers, inclusive transações e integrações. Receber valores independentes de HTTP quando prático. Não criar Service que apenas encaminhe parâmetros para um Model ou Repository.

## Repository

Isolar consultas, transações e detalhes de persistência quando forem complexos ou quando o framework já adotar esse padrão. Manter Repository específico do domínio e evitar um Repository genérico que conheça áreas de negócio independentes.

## Camadas Complementares

- `config`: carregar ambiente e defaults não sensíveis.
- `middlewares` ou `errors`: mapear erros para HTTP e registrar falhas.
- `schemas` ou `validators`: validar e normalizar entrada.
- `serializers` ou `presenters`: formar a saída sem regra de negócio.
- `database`: compartilhar conexão e configuração técnica, sem consultas específicas de negócio.

Manter essas camadas quando melhorarem a coesão. Não comprimir uma arquitetura parcialmente boa em três arquivos gigantes apenas para obter os nomes MVC.

## Dependências

Fazer a direção principal seguir `route/view -> controller -> service -> model/repository`. Permitir `controller -> model/repository` em CRUD simples quando Service não tiver responsabilidade real. Criar dependências compartilhadas na inicialização da aplicação e evitar estado global mutável e imports circulares.

## Estrutura Adaptável

Usar estrutura por camada para projeto pequeno com uma única capacidade coesa:

```text
src/
  config/
  models/
  views/ ou routes/
  controllers/
  services/
  repositories/
  middlewares/
  app.<ext>
```

Omitir `services/` ou `repositories/` quando não houver responsabilidade concreta.

Quando houver múltiplos domínios, manter as camadas MVC na raiz e subdividir cada uma pelos mesmos domínios:

```text
src/
  models/
    <domain_a>/
    <domain_b>/
  views/ ou routes/
    <domain_a>/
    <domain_b>/
  controllers/
    <domain_a>/
    <domain_b>/
  services/
    <domain_a>/
    <domain_b>/
  repositories/
    <domain_a>/
    <domain_b>/
  shared/{config,database,errors}
  app.<ext>
```

Não criar `modules/`. Omitir `services/`, `repositories/` ou subpastas vazias quando não houver responsabilidade concreta. Respeitar convenções obrigatórias do framework, mas preservar a mesma identificação de domínio em cada camada.

Quando dois domínios usarem o mesmo banco, compartilhar conexão e configuração técnica, não um Repository genérico com regras das duas áreas.

## Critérios De Conclusão

- Nenhuma Route/View acessa o banco diretamente, salvo health check deliberadamente simples e documentado.
- Nenhum Model ou Repository conhece request/response HTTP.
- Controllers finos delegam regras reutilizáveis a Services.
- Services não funcionam apenas como repasse entre Controller e Model/Repository.
- Controllers, Services, Models e Repositories de domínios diferentes ficam em subpastas distintas dentro das respectivas camadas MVC.
- Uma área expõe funções ou Services públicos e não importa Controllers internos de outro domínio.
- Configuração sensível vem do ambiente e não aparece em respostas ou logs.
- Operações com várias etapas são atômicas.
- Erros possuem resposta consistente e logs internos seguros.
- Contratos públicos originais continuam cobertos por smoke tests e E2E.
