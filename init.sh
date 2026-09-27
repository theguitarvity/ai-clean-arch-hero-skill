#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
ENGINE_SRC="$SCRIPT_DIR/ai-clean-arch-hero"
ENGINE_DST="$HOME/.ai-clean-arch-hero-engine"
MARKER_FILE="$ENGINE_DST/.managed-by-ai-clean-arch-hero-init"

log() { printf '[clean-arch-hero init] %s\n' "$1"; }
die() { printf '[clean-arch-hero init] ERROR: %s\n' "$1" >&2; exit 1; }

install_engine() {
  [ -f "$ENGINE_SRC/PROTOCOL.md" ] || die "ai-clean-arch-hero/PROTOCOL.md not found."
  mkdir -p "$ENGINE_DST"
  if command -v rsync >/dev/null 2>&1; then
    rsync -a --delete --exclude ".managed-by-ai-clean-arch-hero-init" "$ENGINE_SRC"/ "$ENGINE_DST"/
  else
    rm -rf "${ENGINE_DST:?}"/*
    cp -a "$ENGINE_SRC"/. "$ENGINE_DST"/
  fi
  printf 'installed from %s\n' "$SCRIPT_DIR" > "$MARKER_FILE"
  log "engine mirrored to $ENGINE_DST"
}

write_skill_pointer() {
  local target_dir="$1"
  mkdir -p "$target_dir"
  cat > "$target_dir/SKILL.md" <<EOF
---
name: ai-clean-arch-hero-skill
description: Refatorar projetos existentes progressivamente em direção a Clean Architecture, DDD e boas práticas, preservando comportamento.
---

# AI Clean Arch Hero Skill

Leia e siga integralmente:

    $ENGINE_DST/PROTOCOL.md

Use o core determinístico:

    python3 $ENGINE_DST/lib/cli.py <command> --project <project-root>

Fluxo turbo:

discover -> assess -> plan -> refactor em pequenos lotes -> check -> validate-architecture -> report
EOF
}

install_global_entrypoints() {
  write_skill_pointer "$HOME/.codex/skills/ai-clean-arch-hero-skill"
  write_skill_pointer "$HOME/.agents/skills/ai-clean-arch-hero-skill"
  write_skill_pointer "$HOME/.claude/skills/ai-clean-arch-hero-skill"
  mkdir -p "$HOME/.claude/commands" "$HOME/.config/opencode/commands" "$HOME/.copilot/skills/ai-clean-arch-hero-skill"
  cp "$SCRIPT_DIR/adapters/claude-code.md" "$HOME/.claude/commands/clean-arch-hero.md"
  cp "$SCRIPT_DIR/adapters/opencode-qwen.md" "$HOME/.config/opencode/commands/clean-arch-hero.md"
  write_skill_pointer "$HOME/.copilot/skills/ai-clean-arch-hero-skill"
  log "global entrypoints installed for Codex, Claude Code, Copilot and OpenCode/Qwen-compatible shells"
}

link_project() {
  local project="${1:-$PWD}"
  mkdir -p "$project/.agents/skills/ai-clean-arch-hero-skill" "$project/.github/skills/ai-clean-arch-hero-skill"
  write_skill_pointer "$project/.agents/skills/ai-clean-arch-hero-skill"
  write_skill_pointer "$project/.github/skills/ai-clean-arch-hero-skill"
  python3 "$ENGINE_DST/lib/cli.py" init --project "$project" >/dev/null
  log "project linked at $project"
}

case "${1:-install}" in
  install)
    install_engine
    install_global_entrypoints
    link_project "$PWD"
    ;;
  --engine-only)
    install_engine
    install_global_entrypoints
    ;;
  link)
    install_engine
    link_project "${2:-$PWD}"
    ;;
  *)
    die "usage: ./init.sh [install|--engine-only|link <project>]"
    ;;
esac
