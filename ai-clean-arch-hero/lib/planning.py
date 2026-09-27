from __future__ import annotations

from pathlib import Path
from typing import Any

import architecture_policy


def assess(discovery: dict[str, Any]) -> dict[str, Any]:
    languages = discovery.get("languages", {})
    markers = set(discovery.get("architecture_markers", []))
    has_tests = discovery.get("test_file_count", 0) > 0
    has_domain = "domain" in markers
    has_application = "application" in markers or "usecases" in markers or "usecase" in markers
    has_infra = "infrastructure" in markers or "infra" in markers or "adapters" in markers
    risks = []
    if not has_tests:
        risks.append("No test files detected; start with characterization tests.")
    if discovery.get("git", {}).get("dirty"):
        risks.append("Working tree has existing changes; avoid touching unrelated files.")
    if not discovery.get("commands"):
        risks.append("No quality gates detected from manifests; ask user for build/test commands.")
    if len(languages) > 2:
        risks.append("Multiple languages detected; split batches by runtime boundary.")
    smells = []
    for file in discovery.get("large_files", [])[:10]:
        smells.append({"type": "large_file_candidate", "file": file, "reason": "High size relative to project."})
    return {
        "clean_arch_readiness": {
            "domain_layer_detected": has_domain,
            "application_layer_detected": has_application,
            "infrastructure_layer_detected": has_infra,
            "tests_detected": has_tests,
        },
        "candidate_contexts": discovery.get("candidate_bounded_contexts") or _candidate_contexts(discovery),
        "architecture_contract": {
            "policy": "clean-architecture-contract",
            "recommended_scaffold": discovery.get("project_classification", {}).get("recommended_scaffold", "layer-first"),
            "empty_directories": "forbidden",
            "note": "Clean Architecture is enforced by dependency direction and responsibilities, not directories alone.",
        },
        "smells": smells,
        "risks": risks,
        "recommended_first_move": (
            "Create characterization tests before refactoring."
            if not has_tests
            else "Refactor one high-value flow behind tests."
        ),
    }


def _candidate_contexts(discovery: dict[str, Any]) -> list[dict[str, str]]:
    roots = discovery.get("source_roots", [])
    contexts = []
    for root in roots[:8]:
        label = Path(root).name.replace("_", " ").replace("-", " ").title()
        contexts.append({"name": label, "path": root, "confidence": "LOW"})
    return contexts


def create_plan(discovery: dict[str, Any], assessment: dict[str, Any], max_batches: int = 5) -> dict[str, Any]:
    commands = discovery.get("commands", [])
    blocking = [c for c in commands if str(c.get("blocking")).lower() == "true"]
    large_files = discovery.get("large_files", [])
    batches = []
    if not assessment.get("clean_arch_readiness", {}).get("tests_detected"):
        batches.append({
            "id": "B001",
            "title": "Baseline behavior characterization",
            "lead_role": "test_agent",
            "scope": large_files[:3],
            "goal": "Capture current behavior before structural changes.",
            "allowed_changes": ["tests", "test fixtures", "non-production helpers"],
            "rollback": "Remove the new characterization tests.",
            "gates": blocking,
        })
    batches.append({
        "id": f"B{len(batches) + 1:03d}",
        "title": "Architecture map and boundary naming",
        "lead_role": "architecture_scout",
        "scope": discovery.get("source_roots", [])[:6],
        "goal": "Document current boundaries and name candidate Clean Architecture layers.",
        "allowed_changes": ["docs", "architecture notes", "non-runtime metadata"],
        "rollback": "Revert generated docs/notes.",
        "gates": [],
    })
    for file in large_files[: max(1, max_batches - len(batches))]:
        batches.append({
            "id": f"B{len(batches) + 1:03d}",
            "title": f"Small refactor around {file}",
            "lead_role": "refactoring_agent",
            "scope": [file],
            "goal": "Reduce nesting/complexity and extract clearer domain/application seams while preserving behavior.",
            "allowed_changes": ["production code", "unit tests", "imports", "small docs"],
            "rollback": "Revert this batch diff only.",
            "gates": blocking,
        })
        if len(batches) >= max_batches:
            break
    return {
        "strategy": "turbo-small-batches",
        "architecture_contract": {
            "scaffold": discovery.get("project_classification", {}).get("recommended_scaffold", "layer-first"),
            "must_generate_before_after_map": True,
            "must_run_architecture_gate_per_batch": True,
            "must_discover_bounded_contexts_before_moves": True,
        },
        "parallel_policy": "worktrees_only_independent_scopes",
        "batches": batches[:max_batches],
    }


def architecture_validation(discovery: dict[str, Any]) -> dict[str, Any]:
    project_root = discovery.get("project_root", ".")
    result = architecture_policy.validate_project(project_root, discovery)
    markers = set(discovery.get("architecture_markers", []))
    findings = []
    if "domain" not in markers:
        findings.append({"severity": "INFO", "message": "No explicit domain layer detected yet."})
    if not ({"application", "usecase", "usecases"} & markers):
        findings.append({"severity": "INFO", "message": "No explicit application/use-case layer detected yet."})
    if not ({"infrastructure", "infra", "adapters"} & markers):
        findings.append({"severity": "INFO", "message": "No explicit infrastructure/adapters layer detected yet."})
    result["findings"].extend(findings)
    if result["status"] == "PASSED" and findings:
        result["status"] = "PASSED_WITH_NOTES"
    return result
