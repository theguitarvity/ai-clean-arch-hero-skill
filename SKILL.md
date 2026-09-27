---
name: ai-clean-arch-hero-skill
description: Refatorar projetos existentes progressivamente em direção a Clean Architecture, DDD e boas práticas, preservando comportamento com gates, rastreabilidade e rollback seguro.
---

# AI Clean Arch Hero Skill

Use esta skill quando o usuário pedir para modernizar, reorganizar ou
refatorar um projeto existente em direção a Clean Architecture + DDD,
preservando comportamento.

Antes de agir:

1. Leia `ai-clean-arch-hero/PROTOCOL.md` por inteiro.
2. Rode o discovery determinístico com:
   `python3 ai-clean-arch-hero/lib/cli.py discover --project <project-root>`.
3. Leia/consulte o contrato machine-readable com:
   `python3 ai-clean-arch-hero/lib/cli.py policy`.
4. Nunca refatore tudo em uma única alteração. Trabalhe em lotes pequenos,
   com baseline, quality gates, relatório e rollback claro.

Fluxo obrigatório:

`discover -> assess -> plan -> refactor batch -> check -> architecture validation -> report`

Regras centrais:

- Preserve comportamento observável.
- Prefira early return e menor nesting quando melhorar a leitura.
- Reduza complexidade e code smells sem aplicar dogmas cegamente.
- Evite loops encadeados quando uma decomposição clara, pipeline ou query
  legível for melhor.
- Use no máximo um `if` por método apenas quando isso simplificar o design.
- Modele linguagem de domínio, bounded contexts, use cases, ports/adapters e
  entidades/value objects onde fizer sentido.
- Trate Clean Architecture como regras de dependência e responsabilidade, não
  como árvore de diretórios. Não crie diretórios vazios ou cerimoniais.
- Para projetos pequenos, prefira scaffold layer-first; para médios/grandes,
  prefira feature-first por bounded context. Descubra features/contextos antes
  de mover código e não transforme `shared` em depósito genérico.
- Ports são definidos no core/application; adapters concretos ficam fora do
  core, tipicamente em infrastructure.
- Domain não pode depender de framework, HTTP, banco, ORM, messaging/cache,
  infrastructure ou presentation. Application não pode depender de
  infrastructure nem código framework-specific.
- Adicione ou ajuste testes simples e legíveis; use nested classes quando o
  framework suportar e cenários BDD quando isso tornar o comportamento mais
  claro.
- Execução paralela só em worktrees/áreas independentes, com integração
  controlada.

O engine e os templates ficam em `ai-clean-arch-hero/`.
