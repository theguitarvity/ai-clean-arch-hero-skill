# Generic Agent Adapter

Any coding agent can run AI Clean Arch Hero by reading:

```text
~/.ai-clean-arch-hero-engine/PROTOCOL.md
```

Then call:

```bash
python3 ~/.ai-clean-arch-hero-engine/lib/cli.py discover --project <project>
python3 ~/.ai-clean-arch-hero-engine/lib/cli.py assess --project <project>
python3 ~/.ai-clean-arch-hero-engine/lib/cli.py plan --project <project>
```

The agent implements one batch, records traceability, runs checks, validates
architecture and reports. Parallel execution requires independent worktrees.
