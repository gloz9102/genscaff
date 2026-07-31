#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import random
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "evals" / "cases.json"
RUBRIC = ROOT / "evals" / "rubric.json"
DIMENSIONS = ("functional_completeness", "efficiency", "project_fit", "visual_hierarchy", "responsive_accessibility")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def stable_int(*parts: str) -> int:
    return int(hashlib.sha256("\0".join(parts).encode()).hexdigest()[:16], 16)


def prepare(args: argparse.Namespace) -> int:
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        raise ValueError(f"output directory is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    cases = read_json(CASES)["cases"]
    selected = [case for case in cases if args.suite == "release" or case.get("pr")]
    repeats = 3 if args.suite == "release" else 1
    runs = []
    for case in selected:
        for replicate in range(1, repeats + 1):
            pair_id = f"{case['id']}-r{replicate}"
            for condition in ("control", "treatment"):
                run_id = f"{pair_id}-{condition}"
                run_dir = output / "runs" / run_id
                run_dir.mkdir(parents=True)
                instruction = case["brief"]
                if condition == "treatment":
                    instruction = "Use $genscaff in Standard mode. " + instruction
                (run_dir / "prompt.txt").write_text(instruction + "\n", encoding="utf-8")
                runs.append({
                    "run_id": run_id, "pair_id": pair_id, "case_id": case["id"],
                    "page_type": case["type"], "replicate": replicate,
                    "condition": condition, "workspace": f"runs/{run_id}/workspace",
                    "prompt": f"runs/{run_id}/prompt.txt"
                })
    write_json(output / "manifest.json", {
        "schema_version": 1, "suite": args.suite, "model": args.model,
        "reasoning": args.reasoning, "runs": runs
    })
    print(f"PREPARED_RUNS={len(runs)}")
    return 0


def run(args: argparse.Namespace) -> int:
    root = args.run_dir.resolve()
    manifest = read_json(root / "manifest.json")
    codex = shutil.which("codex")
    git = shutil.which("git")
    if not codex or not git:
        raise RuntimeError("codex and git must be available on PATH")
    failures = 0
    for item in manifest["runs"]:
        run_root = root / "runs" / item["run_id"]
        workspace = root / item["workspace"]
        if (run_root / "result.json").exists() and not args.rerun:
            continue
        workspace.mkdir(parents=True, exist_ok=True)
        subprocess.run([git, "init", "--quiet"], cwd=workspace, check=True)
        prompt = (root / item["prompt"]).read_text(encoding="utf-8")
        command = [
            codex, "exec", "--ephemeral", "--ignore-user-config", "--ignore-rules",
            "--sandbox", "workspace-write", "--model", manifest["model"],
            "-c", f"model_reasoning_effort={manifest['reasoning']}", "--json", prompt,
        ]
        trace = run_root / "trace.jsonl"
        with trace.open("w", encoding="utf-8") as stream:
            completed = subprocess.run(command, cwd=workspace, stdout=stream, stderr=subprocess.PIPE, text=True, check=False)
        write_json(run_root / "result.json", {
            "schema_version": 1, "exit_code": completed.returncode,
            "stderr": completed.stderr[-4000:], "argv": command[1:-1]
        })
        failures += completed.returncode != 0
    print(f"RUN_FAILURES={failures}")
    return 1 if failures else 0


def artifact_summary(run_root: Path) -> dict:
    workspace = run_root / "workspace"
    files = []
    if workspace.is_dir():
        files = sorted(str(path.relative_to(workspace)).replace("\\", "/") for path in workspace.rglob("*") if path.is_file() and ".git" not in path.parts)
    shots = [name for name in files if Path(name).suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}]
    result = read_json(run_root / "result.json") if (run_root / "result.json").is_file() else {"exit_code": None}
    return {"exit_code": result.get("exit_code"), "files": files, "screenshots": shots}


def blind(args: argparse.Namespace) -> int:
    root = args.run_dir.resolve()
    manifest = read_json(root / "manifest.json")
    by_pair: dict[str, list[dict]] = {}
    for item in manifest["runs"]:
        by_pair.setdefault(item["pair_id"], []).append(item)
    packets = []
    for pair_id, items in sorted(by_pair.items()):
        if len(items) != 2:
            raise ValueError(f"pair must contain two conditions: {pair_id}")
        ordered = sorted(items, key=lambda item: item["condition"])
        if stable_int(pair_id, "v2") % 2:
            ordered.reverse()
        packet_id = hashlib.sha256(pair_id.encode()).hexdigest()[:12]
        packets.append({
            "packet_id": packet_id,
            "left": artifact_summary(root / "runs" / ordered[0]["run_id"]),
            "right": artifact_summary(root / "runs" / ordered[1]["run_id"]),
            "human_review_required": stable_int(pair_id, "human") % 5 == 0,
        })
        write_json(root / "private" / f"{packet_id}.json", {"left": ordered[0]["condition"], "right": ordered[1]["condition"], "pair_id": pair_id})
    write_json(root / "blind" / "packets.json", {"schema_version": 1, "packets": packets})
    print(f"BLIND_PACKETS={len(packets)}")
    return 0


def valid_judgment(value: dict) -> bool:
    return value.get("winner") in {"left", "right", "tie"} and all(isinstance(value.get("scores", {}).get(side, {}).get(dimension), int) and 0 <= value["scores"][side][dimension] <= 5 for side in ("left", "right") for dimension in DIMENSIONS)


def score(args: argparse.Namespace) -> int:
    root = args.run_dir.resolve()
    packets = read_json(root / "blind" / "packets.json")["packets"]
    rows = []
    for packet in packets:
        packet_id = packet["packet_id"]
        forward_path = root / "judgments" / f"{packet_id}-forward.json"
        swapped_path = root / "judgments" / f"{packet_id}-swapped.json"
        if not forward_path.is_file() or not swapped_path.is_file():
            continue
        forward, swapped = read_json(forward_path), read_json(swapped_path)
        if not valid_judgment(forward) or not valid_judgment(swapped):
            raise ValueError(f"invalid judgment: {packet_id}")
        inverted = {"left": "right", "right": "left", "tie": "tie"}[swapped["winner"]]
        disagreement = forward["winner"] != inverted
        human_path = root / "judgments" / f"{packet_id}-human.json"
        human = read_json(human_path) if human_path.is_file() else None
        winner = human["winner"] if human else (None if disagreement else forward["winner"])
        rows.append({"packet_id": packet_id, "winner": winner, "judge_disagreement": disagreement, "human_adjudicated": bool(human)})
    write_json(root / "summary.json", {"schema_version": 1, "pairs_scored": len(rows), "results": rows})
    print(f"SCORED_PAIRS={len(rows)}")
    return 0


def validate(args: argparse.Namespace) -> int:
    root = args.run_dir.resolve()
    errors = []
    manifest = read_json(root / "manifest.json")
    expected = 16 if manifest.get("suite") == "pr" else 120
    if len(manifest.get("runs", [])) != expected:
        errors.append(f"expected {expected} runs")
    if any(item.get("condition") not in {"control", "treatment"} for item in manifest.get("runs", [])):
        errors.append("invalid condition")
    blind_path = root / "blind" / "packets.json"
    if blind_path.is_file():
        serialized = blind_path.read_text(encoding="utf-8")
        forbidden = ("control", "treatment", str(root), "workspace", "prompt.txt")
        if any(value in serialized for value in forbidden):
            errors.append("blind packet leaks condition or internal path")
    summary_path = root / "summary.json"
    if summary_path.is_file():
        summary = read_json(summary_path)
        for row in summary.get("results", []):
            if row.get("judge_disagreement") and not row.get("human_adjudicated"):
                errors.append(f"human adjudication required: {row.get('packet_id')}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("EVAL_RUN_VALID")
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Prepare, run, blind, score, and validate Genscaff evaluations")
    commands = root.add_subparsers(dest="command", required=True)
    p = commands.add_parser("prepare")
    p.add_argument("--suite", choices=("pr", "release"), required=True)
    p.add_argument("--model", required=True)
    p.add_argument("--reasoning", choices=("low", "medium", "high", "xhigh"), required=True)
    p.add_argument("--output", type=Path, required=True)
    p.set_defaults(func=prepare)
    p = commands.add_parser("run")
    p.add_argument("--run-dir", type=Path, required=True)
    p.add_argument("--rerun", action="store_true")
    p.set_defaults(func=run)
    for name, function in (("blind", blind), ("score", score), ("validate", validate)):
        p = commands.add_parser(name)
        p.add_argument("--run-dir", type=Path, required=True)
        p.set_defaults(func=function)
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        return args.func(args)
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
