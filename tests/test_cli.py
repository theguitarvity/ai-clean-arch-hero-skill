from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "ai-clean-arch-hero" / "lib" / "cli.py"


class CleanArchHeroCliTests(unittest.TestCase):
    def run_cli(self, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["python3", str(CLI), *args],
            cwd=str(cwd or ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_discover_detects_python_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")
            (root / "src").mkdir()
            (root / "src" / "service.py").write_text("def run():\n    return 1\n", encoding="utf-8")
            proc = self.run_cli("discover", "--project", str(root))
            self.assertEqual(proc.returncode, 0, proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["languages"], {"python": 1})
            self.assertTrue(any(c["command"] == "python3 -m pytest" for c in payload["commands"]))
            self.assertEqual(payload["project_classification"]["recommended_scaffold"], "layer-first")

    def test_plan_creates_small_batches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "package.json").write_text('{"scripts":{"test":"jest"}}\n', encoding="utf-8")
            (root / "src").mkdir()
            (root / "src" / "orders.ts").write_text("export const x = 1\n", encoding="utf-8")
            proc = self.run_cli("plan", "--project", str(root), "--max-batches", "3")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertLessEqual(len(payload["batches"]), 3)
            self.assertEqual(payload["strategy"], "turbo-small-batches")
            self.assertTrue(payload["architecture_contract"]["must_run_architecture_gate_per_batch"])

    def test_architecture_validation_blocks_domain_infrastructure_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            domain = root / "src" / "domain"
            domain.mkdir(parents=True)
            (domain / "user.py").write_text("from src.infrastructure.db import UserRow\n\nclass User:\n    pass\n", encoding="utf-8")
            infra = root / "src" / "infrastructure"
            infra.mkdir(parents=True)
            (infra / "db.py").write_text("class UserRow:\n    pass\n", encoding="utf-8")
            proc = self.run_cli("discover", "--project", str(root))
            self.assertEqual(proc.returncode, 0, proc.stderr)
            proc = self.run_cli("validate-architecture", "--project", str(root))
            self.assertEqual(proc.returncode, 0, proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["status"], "FAILED")
            self.assertTrue(any("Domain cannot depend on infrastructure" in f["message"] for f in payload["findings"]))

    def test_policy_command_returns_machine_readable_contract(self) -> None:
        proc = self.run_cli("policy")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["name"], "clean-architecture-contract")
        self.assertEqual(payload["scaffold_policy"]["empty_directories"], "forbidden")

    def test_report_writes_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "go.mod").write_text("module demo\n", encoding="utf-8")
            (root / "main.go").write_text("package main\n", encoding="utf-8")
            report = root / "hero-report.md"
            proc = self.run_cli("discover", "--project", str(root))
            self.assertEqual(proc.returncode, 0, proc.stderr)
            proc = self.run_cli("report", "--project", str(root), "--output", str(report))
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("AI Clean Arch Hero Report", report.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
