# Diretrizes De Containerização Para E2E

Usar Docker Compose como executor preferencial quando a aplicação e suas dependências forem containerizáveis. Não torná-lo requisito artificial para projetos que já possuam isolamento equivalente mais simples.

## Decisão

1. Reutilizar Compose e Dockerfile existentes quando forem adequados para teste.
2. Criar `compose.e2e.yml` e, se necessário, `Dockerfile.e2e` somente depois da aprovação da Fase 3.
3. Usar execução nativa isolada quando Docker não estiver disponível ou não agregar isolamento.
4. Registrar `NÃO EXECUTADO` quando nenhuma estratégia puder ser executada.

Não codificar linguagem, framework, banco, porta ou endpoint na skill. Derivar tudo dos manifestos, configurações e contratos encontrados.

## Serviços Do Compose

Incluir somente capacidades necessárias:

- aplicação sob teste;
- banco, cache, fila ou broker realmente usados;
- migrations/seed como comando ou serviço de execução única;
- stubs para integrações externas que participem dos cenários.

Evitar containers decorativos e serviços de produção não necessários ao contrato testado.

## Requisitos Técnicos

- Fixar versões de imagens; não usar `latest`.
- Adicionar healthcheck à aplicação e dependências.
- Usar `depends_on` com condição de saúde quando suportado, sem substituir readiness real.
- Passar configuração por variáveis de ambiente sem segredos reais.
- Usar rede e volumes nomeados especificamente para E2E.
- Tornar porta externa configurável e evitar assumir que `3000`, `5000` ou outra esteja livre.
- Executar como usuário não root quando a imagem permitir.
- Adicionar `.dockerignore` coerente com a stack.

## Ciclo Reproduzível

Validar a configuração antes de executar:

```bash
docker compose -f compose.e2e.yml config
```

Executar build limpo quando mudanças de dependência ou imagem puderem afetar o resultado. Aguardar healthcheck, aplicar migrations/seed e iniciar os testes. Ao final, remover apenas recursos do projeto E2E:

```bash
docker compose -f compose.e2e.yml down --volumes --remove-orphans
```

Não usar nomes globais fixos nem comandos de remoção amplos.

## Compatibilidade

- Para SQLite, usar arquivo ou volume temporário; não exigir container de banco.
- Para bancos externos, usar serviço e credenciais exclusivos de teste.
- Para monorepos, limitar build context e serviços ao componente em auditoria.
- Para múltiplas aplicações, declarar dependências e contratos entre serviços explicitamente.
- Para CI, evitar TTY, interação manual e portas publicadas quando a rede interna bastar.
