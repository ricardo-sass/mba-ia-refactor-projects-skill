# Análise De Projeto

## Inventário

1. Localizar manifestos e lockfiles: `requirements*.txt`, `pyproject.toml`, `Pipfile`, `package.json`, lockfiles, `go.mod`, `pom.xml`, `build.gradle`, `Gemfile`, `composer.json` e equivalentes.
2. Excluir dependências e artefatos: `.git`, `node_modules`, ambientes virtuais, caches, `dist`, `build`, coverage, bancos e arquivos gerados.
3. Identificar entry points por scripts de manifesto, blocos main, factories, servidores HTTP, containers e documentação.
4. Ler rotas e controladores antes de inferir o domínio. Confirmar entidades por modelos, schemas, migrations e nomes de endpoints.
5. Agrupar arquivos por capacidade de negócio, linguagem, regras e dados alterados em conjunto. Mapear o proprietário de cada route, controller, service, model e repository sem assumir que cada entidade forma um domínio.
6. Localizar especificações de contrato, testes E2E, Dockerfile, Compose, healthchecks, migrations, seeds e configuração de CI.

## Detecção Da Stack

| Evidência | Inferência |
|---|---|
| `Flask`, decorators `route`, `flask run` | Python + Flask |
| `FastAPI`, `APIRouter`, uvicorn | Python + FastAPI |
| `express()`, Router, `app.listen` | Node.js + Express |
| `@Controller`, NestFactory | TypeScript + NestJS |
| `spring-boot`, `@RestController` | Java + Spring Boot |
| `sqlite3`, URI `sqlite:` | SQLite |
| SQLAlchemy models/session | SQLAlchemy ORM |
| drivers e SQL literal | Acesso SQL direto |

Relatar versão apenas quando manifesto, lockfile ou runtime fornecer evidência. Dizer `não determinada` em vez de adivinhar.

## Mapeamento Arquitetural

Classificar a estrutura predominante:

- Monolito sem camadas: entry point, regras e persistência misturados.
- MVC parcial: rotas, modelos ou controladores existem, mas responsabilidades vazam.
- MVC: Route/View fina, Controller coordena e Model/Repository encapsula dados.
- MVC com Services/Repositories: regras e persistência complexa possuem camadas próprias.
- MVC por domínios: Models, Views/Routes e Controllers são as camadas principais e possuem subpastas correspondentes para cada domínio.

Registrar exceções. Um diretório chamado `models` não prova que há separação de responsabilidades.

## Mapeamento De Domínios E Camadas

Para cada capacidade coesa, registrar:

- nome observado na linguagem do projeto e evidência;
- rotas, comandos ou consumidores de entrada;
- casos de uso, regras e transações;
- models, tabelas, repositories e integrações;
- arquivos atualmente proprietários e arquivos compartilhados;
- dependências de entrada e saída com outros domínios.

Tratar como domínio separado quando a capacidade possuir regras, fluxos ou ritmo de mudança próprios. Manter capacidades triviais na mesma área quando separá-las produzir apenas pastas vazias. Marcar arquivos de `controllers`, `services` ou `repositories` que atendam a vários domínios independentes sem separação clara.

## Contratos E Linha De Base

Mapear para cada endpoint: método, caminho, entrada, status principal, formato de resposta e efeito persistente. Identificar health check e dados de seed. Obter os comandos de install, seed, test e start da documentação e dos manifestos.

Contar arquivos com busca por extensões da stack e informar o critério. Contar linhas com ferramenta local, excluindo lockfiles e arquivos gerados. Não alterar nem inicializar bancos durante as fases 1 e 2 quando isso puder mudar o projeto.

## Resumo Obrigatório

Informar:

- Projeto
- Linguagem e versão
- Framework e versão
- Dependências relevantes
- Banco de dados
- Domínio
- Domínios coesos e distribuição pelas camadas MVC
- Arquitetura atual
- Perfil MVC recomendado e evidências
- Fontes de contrato encontradas
- Estratégia E2E disponível ou proposta
- Arquivos-fonte analisados
- Quantidade aproximada de linhas-fonte
- Ponto de entrada
- Comando de teste ou `não encontrado`
- Comando de inicialização
