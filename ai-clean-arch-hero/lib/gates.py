from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


def run(project: str | Path, commands: list[dict[str, Any]], execute: bool = False) -> list[dict[str, Any]]:
    results = []
    for gate in commands:
        command = gate["command"]
        if not execute:
            results.append({**gate, "status": "PLANNED", "executed": False})
            continue
        proc = subprocess.run(
            command,
            cwd=str(project),
            shell=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=600,
            check=False,
        )
        results.append({
            **gate,
            "status": "PASSED" if proc.returncode == 0 else "FAILED",
            "executed": True,
            "returncode": proc.returncode,
            "output_tail": proc.stdout[-4000:],
        })
    return results
