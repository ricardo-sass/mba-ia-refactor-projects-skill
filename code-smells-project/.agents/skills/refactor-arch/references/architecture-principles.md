# Princípios Arquiteturais MVC

Usar este guia para escolher a menor estrutura MVC que separe entrada, fluxo, regras e persistência sem criar camadas vazias.

## Perfis MVC

| Perfil | Sinais | Estrutura-alvo |
|---|---|---|
| MVC essencial | CRUD pequeno, poucas regras e persistência simples | Model + View/Route + Controller |
| MVC com Services/Repositories | regras reutilizáveis, transações, integrações ou consultas complexas | Model + View/Route + Controller + Service/Repository |
| MVC por domínios | múltiplas capacidades com evolução independente | pastas MVC principais, cada uma subdividida pelos mesmos domínios |

Classificar por evidência. Não criar Service ou Repository que apenas repasse uma chamada sem acrescentar regra, isolamento ou testabilidade.

## Domínios Dentro Das Camadas MVC

Identificar capacidades de negócio pela linguagem, regras, fluxos, dados alterados em conjunto e motivos de mudança. Não considerar cada tabela, entidade ou endpoint um domínio independente.

Organizar primeiro pelas camadas MVC. Quando houver múltiplas capacidades coesas, criar subpastas de domínio correspondentes dentro de cada camada:

- `models/<domain>/` para dados, validações e persistência simples;
- `views/<domain>/` ou `routes/<domain>/` para entrada e saída;
- `controllers/<domain>/` para coordenar o fluxo;
- `services/<domain>/` para regras e orquestrações reutilizáveis, quando necessário;
- `repositories/<domain>/` para persistência complexa, quando necessário;
- testes organizados pelos mesmos domínios ou caminhos equivalentes.

Não criar `modules/`. Evitar arquivos soltos em `controllers`, `services`, `models` ou `repositories` que misturem capacidades independentes. Para um único domínio pequeno, permitir arquivos diretamente nas pastas MVC sem subpastas adicionais.

Integrar áreas por Services ou funções públicas claramente definidas. Não importar Controllers de outro domínio. Manter em `shared` apenas configuração, observabilidade, conexão de banco e utilitários técnicos estáveis, sem mover regras de negócio para lá.

## Direção MVC

Usar como direção principal:

```text
Route/View -> Controller -> Service -> Model/Repository
```

- Permitir `Controller -> Model` em CRUD simples quando um Service seria apenas repasse.
- Manter request, response, status HTTP e serialização em Route/View ou Controller, conforme a convenção do framework.
- Manter SQL e detalhes de persistência em Model ou Repository.
- Manter regras reutilizadas por vários Controllers em Service.
- Criar e injetar clientes externos na inicialização da aplicação quando isso facilitar testes; não exigir interface para toda dependência.

## Auditoria SOLID

| Princípio | Sinais de violação | Direção de correção |
|---|---|---|
| SRP | arquivo mistura protocolo, fluxo, regra, banco e integração | separar por responsabilidade MVC e domínio proprietário |
| OCP | cada novo tipo exige editar condicionais centrais | introduzir estratégia somente quando houver variação real |
| LSP | subtipo exige tratamento especial ou muda o contrato | corrigir a abstração ou preferir composição |
| ISP | consumidor depende de interface extensa e usa poucos métodos | dividir a interface conforme a necessidade do consumidor |
| DIP | Controller ou Service instancia banco, cliente HTTP ou serviço difícil de substituir | receber a dependência por construtor, factory ou parâmetro quando necessário |

Não criar interface com uma única implementação apenas por formalidade. Criá-la somente quando separar uma integração, facilitar teste ou suportar variação real.

## Critérios De Aceite

- Models, Views/Routes e Controllers são as pastas principais da arquitetura.
- Não existe uma pasta `modules/` envolvendo as camadas MVC.
- Cada domínio aparece em subpastas correspondentes das camadas que utiliza.
- Routes/Views tratam entrada e saída sem executar regra de negócio ou SQL.
- Controllers coordenam o fluxo sem concentrar persistência complexa.
- Services possuem regra ou orquestração real; não são camadas de repasse.
- Models/Repositories não conhecem request ou response HTTP.
- Abstrações reduzem acoplamento mensurável sem aumentar arquivos desnecessariamente.
