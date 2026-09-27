#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import discovery as discovery_mod
import gates
import planning
import reporting
from architecture_policy import load_policy
from model import append_trace, ensure_state, save_state, set_status


def print_json(payload) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=False))


def cmd_init(args) -> int:
    state = ensure_state(args.project)
    print_json(state)
    return 0


def cmd_discover(args) -> int:
    state = ensure_state(args.project)
    found = discovery_mod.scan(args.project)
    state["discovery"] = found
    state["gates"] = found.get("commands", [])
    state["metrics"]["source_file_count"] = found.get("source_file_count", 0)
    state["metrics"]["test_file_count"] = found.get("test_file_count", 0)
    set_status(args.project, state, "DISCOVERED")
    append_trace(args.project, {"action": "discover", "summary": "Project discovery completed."})
    print_json(found)
    return 0


def cmd_assess(args) -> int:
    state = ensure_state(args.project)
    if not state.get("discovery"):
        state["discovery"] = discovery_mod.scan(args.project)
    assessment = planning.assess(state["discovery"])
    state["assessment"] = assessment
    set_status(args.project, state, "ASSESSED")
    append_trace(args.project, {"action": "assess", "summary": "Architecture and refactoring assessment completed."})
    print_json(assessment)
    return 0


def cmd_plan(args) -> int:
    state = ensure_state(args.project)
    if not state.get("discovery"):
        state["discovery"] = discovery_mod.scan(args.project)
    if not state.get("assessment"):
        state["assessment"] = planning.assess(state["discovery"])
    plan = planning.create_plan(state["discovery"], state["assessment"], max_batches=args.max_batches)
    state["plan"] = plan
    set_status(args.project, state, "PLANNED")
    append_trace(args.project, {"action": "plan", "summary": f"Created {len(plan['batches'])} turbo batches."})
    print_json(plan)
    return 0


def cmd_check(args) -> int:
    state = ensure_state(args.project)
    if not state.get("discovery"):
        state["discovery"] = discovery_mod.scan(args.project)
    commands = state.get("gates") or state["discovery"].get("commands", [])
    results = gates.run(args.project, commands, execute=args.execute)
    state["last_gate_results"] = results
    set_status(args.project, state, "CHECKING")
    append_trace(args.project, {"action": "check", "summary": f"Quality gates {'executed' if args.execute else 'planned'}."})
    print_json(results)
    return 0


def cmd_validate_architecture(args) -> int:
    state = ensure_state(args.project)
    if not state.get("discovery"):
        state["discovery"] = discovery_mod.scan(args.project)
    result = planning.architecture_validation(state["discovery"])
    state["architecture_validation"] = result
    set_status(args.project, state, "ARCHITECTURE_VALIDATED")
    append_trace(args.project, {"action": "validate_architecture", "summary": result["status"]})
    print_json(result)
    return 0


def cmd_policy(args) -> int:
    print_json(load_policy())
    return 0


def cmd_trace(args) -> int:
    row = append_trace(args.project, {
        "batch": args.batch,
        "action": args.action_name,
        "summary": args.summary,
        "files": args.files.split(",") if args.files else [],
    })
    print_json(row)
    return 0


def cmd_report(args) -> int:
    state = ensure_state(args.project)
    state["status"] = "REPORTED"
    text = reporting.markdown(args.project, state)
    output = Path(args.output) if args.output else Path(args.project) / ".clean-arch-hero" / "report.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")
    state.setdefault("reports", []).append(str(output))
    save_state(args.project, state)
    print(text)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="clean-arch-hero")
    sub = parser.add_subparsers(dest="command", required=True)
    for name, func in [
        ("init", cmd_init),
        ("discover", cmd_discover),
        ("assess", cmd_assess),
        ("validate-architecture", cmd_validate_architecture),
        ("policy", cmd_policy),
    ]:
        p = sub.add_parser(name)
        p.add_argument("--project", default=".")
        p.set_defaults(func=func)
    p = sub.add_parser("plan")
    p.add_argument("--project", default=".")
    p.add_argument("--max-batches", type=int, default=5)
    p.set_defaults(func=cmd_plan)
    p = sub.add_parser("check")
    p.add_argument("--project", default=".")
    p.add_argument("--execute", action="store_true", help="Actually run detected gates.")
    p.set_defaults(func=cmd_check)
    p = sub.add_parser("trace")
    p.add_argument("--project", default=".")
    p.add_argument("--batch", default="")
    p.add_argument("--action-name", default="change")
    p.add_argument("--summary", required=True)
    p.add_argument("--files", default="")
    p.set_defaults(func=cmd_trace)
    p = sub.add_parser("report")
    p.add_argument("--project", default=".")
    p.add_argument("--output")
    p.set_defaults(func=cmd_report)
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
