# Codex Adapter

Use `$ai-clean-arch-hero-skill <project>` or ask Codex to run Clean Arch Hero
in the current repository.

Protocol:

```text
~/.ai-clean-arch-hero-engine/PROTOCOL.md
```

Core commands:

```bash
python3 ~/.ai-clean-arch-hero-engine/lib/cli.py discover --project .
python3 ~/.ai-clean-arch-hero-engine/lib/cli.py assess --project .
python3 ~/.ai-clean-arch-hero-engine/lib/cli.py plan --project .
python3 ~/.ai-clean-arch-hero-engine/lib/cli.py check --project .
python3 ~/.ai-clean-arch-hero-engine/lib/cli.py validate-architecture --project .
python3 ~/.ai-clean-arch-hero-engine/lib/cli.py report --project .
```

Codex should implement one planned batch at a time, run available gates, and
avoid touching unrelated user changes.
