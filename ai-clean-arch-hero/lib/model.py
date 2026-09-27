from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE_DIR = ".clean-arch-hero"
STATE_FILE = "state.json"
TRACE_FILE = "traceability.jsonl"

STATUSES = [
    "INITIALIZED",
    "DISCOVERED",
    "ASSESSED",
    "PLANNED",
    "BATCH_READY",
    "REFACTORING",
    "CHECKING",
    "ARCHITECTURE_VALIDATED",
    "REPORTED",
    "COMPLETED",
    "PAUSED",
    "BLOCKED",
    "FAILED",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def state_path(project: str | Path) -> Path:
    return Path(project) / STATE_DIR / STATE_FILE


def trace_path(project: str | Path) -> Path:
    return Path(project) / STATE_DIR / TRACE_FILE


def ensure_state(project: str | Path) -> dict[str, Any]:
    path = state_path(project)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    state = {
        "version": 1,
        "status": "INITIALIZED",
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "project_root": str(Path(project).resolve()),
        "discovery": {},
        "assessment": {},
        "plan": {"batches": []},
        "gates": [],
        "metrics": {},
        "reports": [],
    }
    save_state(project, state)
    return state


def save_state(project: str | Path, state: dict[str, Any]) -> None:
    if state.get("status") not in STATUSES:
        raise ValueError(f"invalid status: {state.get('status')}")
    state["updated_at"] = utc_now()
    path = state_path(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def set_status(project: str | Path, state: dict[str, Any], status: str) -> dict[str, Any]:
    if status not in STATUSES:
        raise ValueError(f"invalid status: {status}")
    state["status"] = status
    save_state(project, state)
    return state


def append_trace(project: str | Path, row: dict[str, Any]) -> dict[str, Any]:
    row = {"timestamp": utc_now(), **row}
    path = trace_path(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return row


def read_trace(project: str | Path) -> list[dict[str, Any]]:
    path = trace_path(project)
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows
