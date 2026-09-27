from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

IGNORED_DIRS = {
    ".git",
    ".idea",
    ".vscode",
    "node_modules",
    "vendor",
    "dist",
    "build",
    "target",
    ".next",
    ".venv",
    "venv",
    "__pycache__",
    ".clean-arch-hero",
}

MANIFESTS = {
    "package.json": "javascript/typescript",
    "pnpm-lock.yaml": "javascript/typescript",
    "yarn.lock": "javascript/typescript",
    "requirements.txt": "python",
    "pyproject.toml": "python",
    "Pipfile": "python",
    "pom.xml": "java",
    "build.gradle": "java/kotlin",
    "build.gradle.kts": "java/kotlin",
    "go.mod": "go",
    "Cargo.toml": "rust",
    "composer.json": "php",
    "Gemfile": "ruby",
    "*.csproj": "dotnet",
    "*.sln": "dotnet",
}

SOURCE_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".kt": "kotlin",
    ".go": "go",
    ".rs": "rust",
    ".php": "php",
    ".rb": "ruby",
    ".cs": "dotnet",
}

ARCH_NAMES = {
    "domain",
    "application",
    "usecase",
    "usecases",
    "infrastructure",
    "infra",
    "adapter",
    "adapters",
    "ports",
    "entities",
    "repository",
    "repositories",
}

CONTEXT_HINT_DIRS = {
    "modules",
    "features",
    "contexts",
    "bounded-contexts",
    "domains",
    "packages",
    "apps",
    "services",
}


def _git_status(root: Path) -> dict[str, Any]:
    if not (root / ".git").exists():
        return {"is_git_repo": False, "dirty": None, "files": []}
    result = subprocess.run(
        ["git", "-C", str(root), "status", "--short"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    files = [line for line in result.stdout.splitlines() if line.strip()]
    return {"is_git_repo": True, "dirty": bool(files), "files": files[:100]}


def _walk(root: Path) -> tuple[list[Path], list[Path]]:
    manifests: list[Path] = []
    source_files: list[Path] = []
    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        current_path = Path(current)
        for name in files:
            path = current_path / name
            rel = path.relative_to(root)
            if name in MANIFESTS or any(path.match(pattern) for pattern in MANIFESTS if "*" in pattern):
                manifests.append(rel)
            if path.suffix in SOURCE_EXTENSIONS:
                source_files.append(rel)
    return manifests, source_files


def _commands(root: Path, manifests: list[Path]) -> list[dict[str, str]]:
    names = {p.name for p in manifests}
    commands: list[dict[str, str]] = []
    if "package.json" in names:
        commands.extend([
            {"name": "install", "command": "npm install", "blocking": "false"},
            {"name": "test", "command": "npm test", "blocking": "true"},
            {"name": "lint", "command": "npm run lint --if-present", "blocking": "false"},
            {"name": "build", "command": "npm run build --if-present", "blocking": "true"},
        ])
    if "pnpm-lock.yaml" in names:
        commands = [c | {"command": c["command"].replace("npm", "pnpm")} for c in commands]
    if "pyproject.toml" in names or "requirements.txt" in names:
        commands.append({"name": "test", "command": "python3 -m pytest", "blocking": "true"})
    if "pom.xml" in names:
        commands.append({"name": "test", "command": "mvn test", "blocking": "true"})
    if "build.gradle" in names or "build.gradle.kts" in names:
        commands.append({"name": "test", "command": "./gradlew test", "blocking": "true"})
    if "go.mod" in names:
        commands.append({"name": "test", "command": "go test ./...", "blocking": "true"})
    if "Cargo.toml" in names:
        commands.append({"name": "test", "command": "cargo test", "blocking": "true"})
    if "composer.json" in names:
        commands.append({"name": "test", "command": "composer test", "blocking": "true"})
    if "Gemfile" in names:
        commands.append({"name": "test", "command": "bundle exec rake test", "blocking": "true"})
    if any(p.suffix == ".sln" or p.suffix == ".csproj" for p in manifests):
        commands.append({"name": "test", "command": "dotnet test", "blocking": "true"})
    seen = set()
    unique = []
    for command in commands:
        key = (command["name"], command["command"])
        if key not in seen:
            unique.append(command)
            seen.add(key)
    return unique


def scan(project: str | Path) -> dict[str, Any]:
    root = Path(project).resolve()
    manifests, source_files = _walk(root)
    languages: dict[str, int] = {}
    for path in source_files:
        lang = SOURCE_EXTENSIONS.get(path.suffix)
        if lang:
            languages[lang] = languages.get(lang, 0) + 1
    arch_dirs = sorted({
        part
        for path in source_files
        for part in path.parts
        if part.lower() in ARCH_NAMES
    })
    contexts = _bounded_contexts(source_files)
    large_files = sorted(source_files, key=lambda p: (root / p).stat().st_size, reverse=True)[:20]
    test_files = [p for p in source_files if "test" in str(p).lower() or "spec" in str(p).lower()]
    return {
        "project_root": str(root),
        "manifests": [str(p) for p in sorted(manifests)],
        "languages": languages,
        "source_file_count": len(source_files),
        "test_file_count": len(test_files),
        "source_files": [str(p) for p in sorted(source_files)],
        "source_roots": sorted({p.parts[0] for p in source_files if p.parts}),
        "architecture_markers": arch_dirs,
        "candidate_bounded_contexts": contexts,
        "project_classification": _project_classification(len(source_files), contexts),
        "large_files": [str(p) for p in large_files],
        "commands": _commands(root, manifests),
        "git": _git_status(root),
    }


def _bounded_contexts(source_files: list[Path]) -> list[dict[str, Any]]:
    contexts: dict[str, dict[str, Any]] = {}
    for path in source_files:
        parts = path.parts
        for index, part in enumerate(parts[:-1]):
            if part.lower() in CONTEXT_HINT_DIRS and index + 1 < len(parts):
                context_path = Path(*parts[: index + 2])
                key = str(context_path)
                contexts.setdefault(key, {"name": parts[index + 1], "path": key, "source_files": 0, "confidence": "MEDIUM"})
                contexts[key]["source_files"] += 1
                break
        else:
            if len(parts) > 2 and parts[0] == "src" and parts[1] not in ARCH_NAMES:
                key = str(Path(parts[0]) / parts[1])
                contexts.setdefault(key, {"name": parts[1], "path": key, "source_files": 0, "confidence": "LOW"})
                contexts[key]["source_files"] += 1
    return sorted(contexts.values(), key=lambda item: (-item["source_files"], item["path"]))[:20]


def _project_classification(source_count: int, contexts: list[dict[str, Any]]) -> dict[str, str]:
    is_small = source_count <= 120 and len(contexts) <= 3
    return {
        "size": "small" if is_small else "medium_large",
        "recommended_scaffold": "layer-first" if is_small else "feature-first",
        "reason": f"{source_count} source files and {len(contexts)} candidate bounded contexts detected.",
    }
