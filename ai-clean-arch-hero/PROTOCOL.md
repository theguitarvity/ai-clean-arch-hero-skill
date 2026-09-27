# AI Clean Arch Hero Protocol

AI Clean Arch Hero é um orquestrador agentic para refatoração progressiva de
projetos existentes. Ele não promete "reescrever tudo"; ele cria uma rota
segura para mover código real em direção a Clean Architecture, DDD e boas
práticas sem perder comportamento.

## Princípios

1. **Comportamento preservado primeiro**: antes de mover código, descubra
   como build, testes, lint e execução funcionam.
2. **Pequenos lotes reversíveis**: cada batch deve ser compreensível,
   testável e fácil de reverter.
3. **Arquitetura evolutiva**: extraia domain/application/infrastructure por
   fluxo de negócio, não por reestruturação cosmética massiva.
4. **Contrato antes de pastas**: Clean Architecture significa direção de
   dependência e responsabilidades verificáveis. Diretórios só devem existir
   quando houver responsabilidade concreta; diretórios vazios/cerimoniais são
   proibidos.
5. **DDD pragmático**: use linguagem ubíqua, bounded contexts, aggregates,
   value objects, repositories, domain services e domain events somente onde
   o código e o domínio sustentarem.
6. **Boas práticas sem fanatismo**: early return, menor nesting, menor
   complexidade, remoção de smells e métodos simples são metas. A regra de
   "1 if por método" é heurística, não lei.
7. **Multi-linguagem via adapters**: nunca assuma Java. Detecte manifests,
   frameworks, comandos e convenções do projeto.
8. **Determinismo estrutural**: discovery, estado, plano, gates, métricas e
   relatório vêm do engine. A escrita de código fica com o agente.
9. **Rastreabilidade**: cada mudança deve apontar para smell, decisão,
   lote, arquivo, teste e gate.

## Architecture Policy / Grammar

O contrato formal fica em `config/architecture-policy.json` e pode ser lido por:

```bash
python3 ~/.ai-clean-arch-hero-engine/lib/cli.py policy
```

Regras obrigatórias:

- `Presentation -> Application`; presentation faz mapping de protocolo,
  requests/responses, presenters e exception handlers, sem regra de negócio.
- `Infrastructure -> Application`; infrastructure implementa repositories,
  adapters, ORM, APIs externas, messaging, cache, observability e config.
- `Application -> Domain`; application contém use cases, ports, orchestration,
  DTOs necessários, mappers e validators, sem controllers, SQL, Kafka/Redis
  concretos ou código framework-specific.
- `Domain -> nothing external`; domain contém entities, value objects,
  aggregates, domain services/events/exceptions/policies e não depende de
  framework, HTTP, banco, ORM, messaging/cache, infrastructure ou presentation.
- Ports pertencem ao core/application; adapters concretos implementam esses
  ports fora do core. Exemplo: `UserRepository` na Application e
  `PostgresUserRepository` na Infrastructure.
- `Bootstrap` contém DI, startup e wiring, sem regra de negócio.

Scaffold:

- Projetos pequenos usam preferencialmente layer-first:
  `src/domain`, `src/application`, `src/infrastructure`, `src/presentation`,
  `src/bootstrap`, `tests`, `docs`, `scripts`, `config`.
- Projetos médios/grandes usam preferencialmente feature-first:
  `src/modules/<bounded-context>/{domain,application,infrastructure,presentation}`,
  `src/shared/{domain,application,infrastructure}` apenas para abstrações
  realmente compartilhadas, e `src/bootstrap`.
- Antes de mover código, descubra features/bounded contexts existentes. Nunca
  reorganize cegamente e nunca crie `shared` como dumping ground.

## State Machine

Estados do projeto:

```text
INITIALIZED
DISCOVERED
ASSESSED
PLANNED
BATCH_READY
REFACTORING
CHECKING
ARCHITECTURE_VALIDATED
REPORTED
COMPLETED
PAUSED | BLOCKED | FAILED
```

Transições recomendadas:

```text
discover -> assess -> plan -> batch -> refactor -> check -> validate -> report
```

Um agente pode retomar qualquer execução lendo `.clean-arch-hero/state.json`.
Comandos são idempotentes: se o estado já existe, preserve decisões e adicione
novas evidências sem apagar histórico.

## Workflow Turbo

### 1. Discover

Rode:

```bash
python3 ~/.ai-clean-arch-hero-engine/lib/cli.py discover --project .
```

O discovery deve identificar:

- linguagens e manifests;
- frameworks e runners prováveis;
- comandos reais de build/test/lint/typecheck;
- diretórios de source e test;
- sinais de arquitetura;
- arquivos grandes e candidatos a smells;
- status git;
- riscos de refatoração.
- tamanho do projeto e recomendação `layer-first` ou `feature-first`;
- bounded contexts/features candidatos antes de qualquer migração estrutural.

Não invente comandos. Só use comandos detectados em manifests ou já
documentados no repositório.

### 2. Assess

Rode:

```bash
python3 ~/.ai-clean-arch-hero-engine/lib/cli.py assess --project .
```

Classifique:

- bounded contexts candidatos;
- fluxos de negócio;
- acoplamentos problemáticos;
- violações de dependência;
- smells de complexidade;
- lacunas de teste;
- riscos de segurança ou credenciais.

### 3. Plan

Rode:

```bash
python3 ~/.ai-clean-arch-hero-engine/lib/cli.py plan --project . --max-batches 5
```

Cada batch deve conter:

- objetivo;
- escopo de arquivos;
- papel líder;
- testes esperados;
- gates bloqueantes;
- estratégia de rollback;
- métrica de sucesso.
- mapa before/after quando houver migração estrutural.

### 4. Refactor Small Batches

Para cada batch:

1. Leia o plano.
2. Faça uma mudança pequena.
3. Mantenha compatibilidade pública.
4. Adicione/adapte testes.
5. Registre decisão em `.clean-arch-hero/traceability.jsonl`.

Ordem segura preferida:

1. caracterização de comportamento;
2. extração de funções puras;
3. portas/interfaces;
4. application services/use cases;
5. domain model;
6. adapters de infraestrutura;
7. limpeza de controllers/handlers;
8. remoção de código morto.

### 5. Test and Quality Gates

Rode:

```bash
python3 ~/.ai-clean-arch-hero-engine/lib/cli.py check --project .
```

Se baseline falhou antes, não transforme isso em sucesso falso. Marque como
`KNOWN_BASELINE_FAILURE` e não piore.

### 6. Architecture Validation

Rode:

```bash
python3 ~/.ai-clean-arch-hero-engine/lib/cli.py validate-architecture --project .
```

Valide:

- dependências apontam para dentro;
- domínio não importa infraestrutura;
- adapters dependem de portas, não o contrário;
- use cases coordenam regras sem saber detalhes externos;
- testes protegem comportamento crítico.
- a policy machine-readable explica toda violação encontrada.

### 7. Report

Rode:

```bash
python3 ~/.ai-clean-arch-hero-engine/lib/cli.py report --project .
```

Inclua:

- batches executados;
- arquivos alterados;
- gates;
- métricas;
- riscos restantes;
- próximos lotes recomendados.

## Papéis Agentic

- **Orchestrator**: mantém estado, escolhe próximo batch, integra resultados.
- **Architecture Scout**: mapeia arquitetura atual, dependências e riscos.
- **DDD Mapper**: identifica linguagem, bounded contexts e modelos.
- **Refactoring Agent**: executa mudanças pequenas e preserva API.
- **Test Agent**: cria testes de caracterização, unitários e BDD.
- **Quality/Security Reviewer**: revisa diffs, gates, segredos e riscos.

## Paralelismo

Execução paralela só é permitida quando:

- cada agente usa worktree próprio ou área independente;
- batches não compartilham arquivos;
- integração é serial;
- o Orchestrator roda gates após integrar cada batch;
- conflitos bloqueiam o batch, não são resolvidos às cegas.

## Regras de Segurança

- Nunca rode comandos destrutivos sem pedido explícito do usuário.
- Nunca sobrescreva mudanças não relacionadas.
- Nunca mova o projeto inteiro de uma vez.
- Nunca copie segredos para relatórios, prompts ou logs.
- Nunca crie arquitetura nova sem evidência no domínio/código.
- Sempre prefira rollback por commit/batch/diff pequeno.

## Adapters

Adapters ficam em `adapters/` e devem apontar para este protocolo e o CLI.
Eles existem para Claude Code, Codex, Copilot, OpenCode/Qwen e fallback
genérico. Outros agentes podem ser adicionados mantendo a mesma interface:

```bash
python3 ~/.ai-clean-arch-hero-engine/lib/cli.py <command> --project <path>
```
