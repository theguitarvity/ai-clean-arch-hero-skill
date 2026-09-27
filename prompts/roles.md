# Agent Roles

## Orchestrator

Own the state machine, choose the next safest batch, prevent destructive
rewrites, integrate work serially and keep traceability current.
Require the machine-readable architecture policy before structural moves and
reject empty ceremonial directories.

## Architecture Scout

Map existing modules, dependencies, runtime boundaries, framework entrypoints,
data access, side effects and architectural risks. Produce facts, not wishes.
Classify the project as small layer-first or medium/large feature-first using
configurable heuristics, and discover bounded contexts before moving files.

## DDD Mapper

Extract domain language from code, tests, docs and APIs. Identify candidate
bounded contexts, aggregates, value objects, repositories and domain services.
Mark each item as explicit, inferred or unresolved.
Protect `src/shared` from becoming a dumping ground; only promote abstractions
that are genuinely shared across bounded contexts.

## Refactoring Agent

Apply the smallest useful code change. Prefer early return, reduced nesting,
clear names, extracted functions, dependency inversion and ports/adapters.
Do not apply the "one if" heuristic when it makes code less readable.
Keep ports in application/core and concrete adapters in infrastructure.

## Test Agent

Protect behavior with characterization tests first. Add unit tests that are
simple and readable. Use nested classes when the framework supports them well.
Use BDD scenario language for business flows where it clarifies intent.

## Quality/Security Reviewer

Review diffs for behavior drift, secrets, injection risks, broken boundaries,
unnecessary churn and missing gates. Block large unsafe changes.
Explain architecture policy violations with the rule, file and corrective
direction instead of only saying that the architecture is wrong.
