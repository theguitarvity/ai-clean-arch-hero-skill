<div align="center">

# AI Clean Arch Hero Skill

**Orquestrador agentic para refatorar projetos existentes rumo a Clean Architecture + DDD sem big-bang rewrite.**

`Python 3 stdlib` · `multi-linguagem via discovery/adapters` · `batches pequenos` · `quality gates` · `rollback seguro` · `Codex/Claude/Copilot/OpenCode`

</div>

---

## Por quê

Refatorar um projeto inteiro para Clean Architecture costuma dar errado quando
vira uma troca massiva de pastas, nomes e camadas. O AI Clean Arch Hero segue
outro caminho: entra no projeto, descobre como ele funciona, cria baseline,
planeja lotes pequenos, protege comportamento com testes/gates e só então move
um fluxo por vez para uma arquitetura mais limpa.

Ele é inspirado na experiência do Spec Master: init global, protocolo
explícito, core determinístico, adapters por agente, estado persistente,
rastreabilidade, métricas e retomada.

## Fluxo Turbo

```text
discover
  -> assess
  -> plan
  -> refactor em pequenos lotes
  -> check / quality gates
  -> architecture validation
  -> report
```

O modo turbo é menor que um Spec Kit completo. Ele prioriza um MVP seguro e
extensível para refatoração real.

## Instalação

No diretório desta skill:

```bash
./init.sh --engine-only
```

Isso espelha o engine para:

```text
~/.ai-clean-arch-hero-engine
```

E instala pointers globais para:

- `~/.codex/skills/ai-clean-arch-hero-skill`
- `~/.agents/skills/ai-clean-arch-hero-skill`
- `~/.claude/skills/ai-clean-arch-hero-skill`
- `~/.claude/commands/clean-arch-hero.md`
- `~/.copilot/skills/ai-clean-arch-hero-skill`
- `~/.config/opencode/commands/clean-arch-hero.md`

Para linkar em um projeto específico:

```bash
./init.sh link /path/to/project
```

## Uso Rápido

Dentro de um projeto:

```bash
python3 ~/.ai-clean-arch-hero-engine/lib/cli.py discover --project .
python3 ~/.ai-clean-arch-hero-engine/lib/cli.py assess --project .
python3 ~/.ai-clean-arch-hero-engine/lib/cli.py plan --project . --max-batches 5
python3 ~/.ai-clean-arch-hero-engine/lib/cli.py policy
```

Depois o agente implementa apenas o próximo batch planejado, registra
rastreabilidade e roda:

```bash
python3 ~/.ai-clean-arch-hero-engine/lib/cli.py check --project .
python3 ~/.ai-clean-arch-hero-engine/lib/cli.py validate-architecture --project .
python3 ~/.ai-clean-arch-hero-engine/lib/cli.py report --project .
```

Para realmente executar gates detectados:

```bash
python3 ~/.ai-clean-arch-hero-engine/lib/cli.py check --project . --execute
```

Sem `--execute`, o comando lista os gates que seriam usados.

## Comandos

| Comando | Função |
|---|---|
| `init` | cria `.clean-arch-hero/state.json` |
| `discover` | detecta manifests, linguagens, testes, comandos e sinais arquiteturais |
| `assess` | identifica riscos, smells e readiness para Clean Architecture |
| `plan` | gera batches pequenos e reversíveis |
| `policy` | imprime o contrato arquitetural machine-readable |
| `trace` | registra uma decisão/mudança no JSONL de rastreabilidade |
| `check` | lista ou executa gates detectados |
| `validate-architecture` | valida sinais de camadas e regras de dependência |
| `report` | gera `.clean-arch-hero/report.md` |

## Regras de Refatoração

- Preserve comportamento observável.
- Crie ou rode baseline antes de mover código.
- Prefira early return quando reduzir nesting.
- Evite loops encadeados quando extração, pipeline ou query legível for melhor.
- Use a regra de "no máximo 1 if por método" como heurística. Não force se
  piorar o design.
- Elimine smells com passos pequenos: método longo, god object, acoplamento de
  infraestrutura, regra de negócio em controller, duplicação e nomes pobres.
- Mova regras para domínio/application por fluxo, não por reorganização
  cosmética.
- Use testes simples; nested classes quando o framework suporta bem; BDD para
  cenários de negócio onde a linguagem ajuda.

## Premissa Arquitetural Obrigatória

Clean Architecture nesta skill é um contrato de dependências e
responsabilidades, não uma troca cosmética de pastas. A policy formal fica em
[`config/architecture-policy.json`](config/architecture-policy.json) e é usada
por `validate-architecture`.

Direção obrigatória:

```text
Presentation -> Application
Infrastructure -> Application
Application -> Domain
Domain -> nothing external
```

Regras por camada:

- **Domain**: entities, value objects, aggregates, domain services, events,
  exceptions e policies. Proibido framework, HTTP, DB/ORM, messaging/cache
  concreto, infrastructure e presentation.
- **Application**: use cases, ports, orchestration, DTOs necessários, mappers
  e validators. Proibido controllers, SQL, Kafka/Redis concreto,
  framework-specific code e dependência de infrastructure.
- **Infrastructure**: implementations de repositories/adapters, ORM, APIs
  externas, messaging, cache, observability, security e config.
- **Presentation**: controllers, protocol mapping, requests/responses,
  presenters e exception handlers. Não contém regra de negócio.
- **Bootstrap**: dependency injection, startup, config e wiring.

Ports são definidos no core/application e adapters são implementados fora do
core. Exemplo: `UserRepository` em Application e `PostgresUserRepository` em
Infrastructure.

## Scaffold Universal

Para projetos pequenos, a recomendação preferencial é layer-first:

```text
src/domain/{entities,value-objects,aggregates,services,events,exceptions,policies}
src/application/{use-cases,ports/inbound,ports/outbound,dto,mappers,validators}
src/infrastructure/{persistence/{repositories,entities,migrations},messaging,cache,http,security,observability,config}
src/presentation/{controllers,requests,responses,presenters,exception-handlers}
src/bootstrap/{dependency-injection,config,main.*}
tests/{unit/{domain,application},integration,architecture,contract,e2e}
docs/{architecture,adr,diagrams}
scripts
config
```

Para projetos médios/grandes, a recomendação preferencial é feature-first:

```text
src/modules/<bounded-context>/{domain,application,infrastructure,presentation}
src/shared/{domain,application,infrastructure}
src/bootstrap
```

Importante: a skill não deve criar diretórios vazios ou cerimoniais. Cada
pasta só existe quando houver responsabilidade concreta. `src/shared` só existe
para abstrações realmente compartilhadas; nunca como depósito genérico.

## Gates Verificáveis

O discovery classifica automaticamente projeto pequeno vs médio/grande com
heurísticas configuráveis, sugere layer-first ou feature-first e lista bounded
contexts candidatos. A skill nunca reorganiza cegamente: toda migração
estrutural deve preservar comportamento, gerar mapa before/after e executar
testes/build/architecture gates por lote.

## Papéis

- **Orchestrator** mantém estado, lote atual, gates e integração.
- **Architecture Scout** mapeia código, dependências e riscos.
- **DDD Mapper** encontra linguagem ubíqua e bounded contexts candidatos.
- **Refactoring Agent** executa mudanças pequenas.
- **Test Agent** protege comportamento.
- **Quality/Security Reviewer** bloqueia diffs perigosos.

Veja [`prompts/roles.md`](prompts/roles.md).

## Segurança

O Clean Arch Hero não deve:

- refatorar tudo em um único diff;
- sobrescrever mudanças não relacionadas;
- rodar comandos destrutivos sem pedido explícito;
- copiar segredos para relatório;
- mascarar baseline quebrado;
- criar camadas sem evidência no domínio.

Execução paralela só em worktrees/escopos independentes, com integração
controlada e gates após cada integração.

## Estrutura

```text
.
├── SKILL.md
├── README.md
├── init.sh
├── ai-clean-arch-hero/
│   ├── PROTOCOL.md
│   └── lib/
│       ├── cli.py
│       ├── discovery.py
│       ├── gates.py
│       ├── model.py
│       ├── planning.py
│       └── reporting.py
├── adapters/
├── config/
├── examples/
├── prompts/
└── tests/
```

## Desenvolvimento

Rodar testes:

```bash
python3 -m unittest discover -s tests -q
```

Smoke test local:

```bash
python3 ai-clean-arch-hero/lib/cli.py discover --project .
python3 ai-clean-arch-hero/lib/cli.py assess --project .
python3 ai-clean-arch-hero/lib/cli.py plan --project .
python3 ai-clean-arch-hero/lib/cli.py report --project .
```

## Roadmap

- Melhorar parser de scripts reais de `package.json`, `pyproject.toml`,
  `composer.json` e similares.
- Adicionar análise de imports por linguagem para validar dependência
  domain/application/infrastructure.
- Gerar worktree plan automático para lotes independentes.
- Criar adapters para Antigravity, Cursor e outros agentes com convenções
  confirmadas.
- Adicionar métricas de complexidade por AST quando houver parser disponível.
- Criar templates de relatório executivo e técnico.
- Integrar baseline de cobertura quando o projeto já tiver ferramenta.
