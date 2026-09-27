from __future__ import annotations

from pathlib import Path
from typing import Any

from model import read_trace


def markdown(project: str | Path, state: dict[str, Any]) -> str:
    trace = read_trace(project)
    discovery = state.get("discovery", {})
    assessment = state.get("assessment", {})
    plan = state.get("plan", {})
    lines = [
        "# AI Clean Arch Hero Report",
        "",
        f"- Status: `{state.get('status')}`",
        f"- Project: `{discovery.get('project_root', state.get('project_root'))}`",
        f"- Languages: `{discovery.get('languages', {})}`",
        f"- Source files: `{discovery.get('source_file_count', 0)}`",
        f"- Test files: `{discovery.get('test_file_count', 0)}`",
        f"- Recommended scaffold: `{discovery.get('project_classification', {}).get('recommended_scaffold', 'unknown')}`",
        "",
        "## Architecture Readiness",
        "",
    ]
    readiness = assessment.get("clean_arch_readiness", {})
    if readiness:
        for key, value in readiness.items():
            lines.append(f"- {key}: `{value}`")
    else:
        lines.append("- Assessment not run yet.")
    lines.extend(["", "## Planned Batches", ""])
    for batch in plan.get("batches", []):
        lines.append(f"- `{batch['id']}` {batch['title']} — {batch['goal']}")
    if not plan.get("batches"):
        lines.append("- No batches planned yet.")
    lines.extend(["", "## Risks", ""])
    for risk in assessment.get("risks", []):
        lines.append(f"- {risk}")
    if not assessment.get("risks"):
        lines.append("- No major risks recorded.")
    validation = state.get("architecture_validation", {})
    if validation:
        lines.extend(["", "## Architecture Policy", ""])
        lines.append(f"- Policy: `{validation.get('policy', 'unknown')}`")
        lines.append(f"- Status: `{validation.get('status', 'unknown')}`")
        for finding in validation.get("findings", [])[:20]:
            location = f" `{finding.get('file')}`" if finding.get("file") else ""
            lines.append(f"- {finding.get('severity', 'INFO')}:{location} {finding.get('message', '')}")
    lines.extend(["", "## Traceability", ""])
    if trace:
        for row in trace[-20:]:
            lines.append(f"- `{row.get('batch', 'n/a')}` {row.get('action', 'change')} — {row.get('summary', '')}")
    else:
        lines.append("- No traceability rows yet.")
    lines.extend(["", "## Next Step", ""])
    lines.append("Run the next planned batch, then execute `check` and `validate-architecture` before continuing.")
    return "\n".join(lines) + "\n"
