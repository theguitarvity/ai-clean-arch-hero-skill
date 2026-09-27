from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ENGINE_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ENGINE_ROOT.parent
POLICY_PATH = SKILL_ROOT / "config" / "architecture-policy.json"

IMPORT_RE = re.compile(r"^\s*(?:from\s+([\w.]+)\s+import|import\s+([\w.]+)|import\s+.*\s+from\s+['\"]([^'\"]+)['\"]|require\(['\"]([^'\"]+)['\"]\))")
TECH_PATTERNS = {
    "domain": [
        ("framework", re.compile(r"\b(Spring|Quarkus|NestJS|Express|FastAPI|Django|Flask|EntityFramework|Hibernate)\b|@(Controller|Service|Entity|Injectable|RestController)\b")),
        ("http", re.compile(r"\b(HttpRequest|HttpResponse|Request|Response|Controller|Route|Router)\b")),
        ("db/orm", re.compile(r"\b(SQL|SELECT|INSERT|UPDATE|DELETE|RepositoryImpl|EntityManager|Prisma|Sequelize|TypeORM|JPA|Jdbc|DbContext)\b", re.I)),
        ("messaging/cache", re.compile(r"\b(Kafka|Rabbit|Redis|SQS|SNS|PubSub|Memcached)\b")),
    ],
    "application": [
        ("controller", re.compile(r"\b(Controller|Route|Router|HttpRequest|HttpResponse)\b")),
        ("sql", re.compile(r"\b(SELECT|INSERT|UPDATE|DELETE|JOIN|EntityManager|DbContext|Prisma|Sequelize|TypeORM|JPA|Jdbc)\b", re.I)),
        ("framework-specific", re.compile(r"\b(Spring|Quarkus|NestJS|Express|FastAPI|Django|Flask)\b|@(Controller|RestController|Injectable|Entity)\b")),
        ("messaging/cache implementation", re.compile(r"\b(KafkaProducer|KafkaConsumer|RedisClient|RabbitTemplate|SqsClient)\b")),
    ],
    "presentation": [
        ("database access", re.compile(r"\b(SELECT|INSERT|UPDATE|DELETE|EntityManager|DbContext|Prisma|RepositoryImpl)\b", re.I)),
    ],
}


def load_policy(path: str | Path | None = None) -> dict[str, Any]:
    policy_path = Path(path) if path else POLICY_PATH
    return json.loads(policy_path.read_text(encoding="utf-8"))


def classify_layer(path: str | Path) -> str | None:
    parts = [p.lower() for p in Path(path).parts]
    for layer in ("domain", "application", "infrastructure", "presentation", "bootstrap"):
        if layer in parts:
            return layer
    if "infra" in parts or "adapters" in parts:
        return "infrastructure"
    if "controllers" in parts or "handlers" in parts:
        return "presentation"
    if "usecases" in parts or "use-cases" in parts or "ports" in parts:
        return "application"
    return None


def recommended_scaffold(discovery: dict[str, Any], policy: dict[str, Any] | None = None) -> dict[str, Any]:
    policy = policy or load_policy()
    small = policy["scaffold_policy"]["small_project"]["heuristics"]
    source_count = int(discovery.get("source_file_count", 0))
    context_count = len(discovery.get("candidate_bounded_contexts", []))
    is_small = source_count <= small["max_source_files"] and context_count <= small["max_candidate_contexts"]
    key = "small_project" if is_small else "medium_large_project"
    return {
        "project_size": "small" if is_small else "medium_large",
        "recommended_style": policy["scaffold_policy"][key]["style"],
        "reason": f"{source_count} source files and {context_count} candidate bounded contexts.",
        "empty_directories": policy["scaffold_policy"]["empty_directories"],
    }


def validate_project(project: str | Path, discovery: dict[str, Any], policy: dict[str, Any] | None = None) -> dict[str, Any]:
    root = Path(project).resolve()
    policy = policy or load_policy()
    source_files = [Path(p) for p in discovery.get("source_files", [])]
    dependency_rules = {rule["from"]: set(rule["allowed_dependencies"]) for rule in policy["dependency_rules"]}
    findings: list[dict[str, Any]] = []
    layer_counts: dict[str, int] = {}

    for rel in source_files:
        layer = classify_layer(rel)
        if not layer:
            continue
        layer_counts[layer] = layer_counts.get(layer, 0) + 1
        path = root / rel
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        imported_layers = _imported_layers(text)
        forbidden_layers = sorted(imported_layers - dependency_rules.get(layer, set()) - {layer})
        for forbidden in forbidden_layers:
            findings.append({
                "severity": "ERROR",
                "rule": f"{layer}_must_not_depend_on_{forbidden}",
                "file": str(rel),
                "message": f"{layer.title()} cannot depend on {forbidden}. Move the dependency behind an application port or adapter boundary.",
            })
        for label, pattern in TECH_PATTERNS.get(layer, []):
            if pattern.search(text):
                findings.append({
                    "severity": "ERROR" if layer in {"domain", "application"} else "WARN",
                    "rule": f"{layer}_forbids_{label.replace('/', '_').replace(' ', '_')}",
                    "file": str(rel),
                    "message": f"{layer.title()} contains {label}; responsibility belongs outside this layer under the Clean Architecture policy.",
                })

    status = "FAILED" if any(f["severity"] == "ERROR" for f in findings) else ("PASSED_WITH_NOTES" if findings else "PASSED")
    return {
        "status": status,
        "policy": policy["name"],
        "scaffold": recommended_scaffold(discovery, policy),
        "layer_file_counts": layer_counts,
        "findings": findings,
        "rule_set": [rule["message"] for rule in policy["dependency_rules"]],
    }


def _imported_layers(text: str) -> set[str]:
    layers: set[str] = set()
    for line in text.splitlines():
        match = IMPORT_RE.search(line)
        if not match:
            continue
        target = next((group for group in match.groups() if group), "")
        normalized = target.replace("@/", "").replace("~/", "").replace("\\", "/").lower()
        for layer in ("domain", "application", "infrastructure", "presentation", "bootstrap"):
            if re.search(rf"(^|[./_-]){layer}([./_-]|$)", normalized):
                layers.add(layer)
        if re.search(r"(^|[./_-])(infra|adapters)([./_-]|$)", normalized):
            layers.add("infrastructure")
    return layers
