#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "evals" / "cases.json"
RUBRIC = ROOT / "evals" / "rubric.json"
CORE_SKILL = ROOT / "plugins" / "genscaff" / "skills" / "genscaff"
DIMENSIONS = tuple(json.loads(RUBRIC.read_text(encoding="utf-8"))["dimensions"])
EXPECTED_FIELDS = {
    "profile", "project_mode", "reference_mode", "experience_archetype",
    "surface_types", "required_references", "required_states", "must_include",
    "must_not_include", "verification_ceiling", "strict_delegation_expected",
    "legacy_compatibility_expected",
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def stable_int(*parts: str) -> int:
    return int(hashlib.sha256("\0".join(parts).encode()).hexdigest()[:16], 16)


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted((path for path in root.rglob("*") if path.is_file() and not any(part in {"__pycache__", "node_modules"} for part in path.parts)), key=lambda value: value.as_posix()):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def validate_definitions() -> list[str]:
    errors = []
    data = read_json(CASES)
    cases = data.get("cases")
    if data.get("schema_version") != 2 or not isinstance(cases, list):
        return ["evals/cases.json must use schema_version 2 with a cases list"]
    ids = [case.get("id") for case in cases if isinstance(case, dict)]
    if len(ids) != len(set(ids)) or any(not isinstance(value, str) or not value for value in ids):
        errors.append("eval case ids must be unique non-empty strings")
    for case in cases:
        if not isinstance(case, dict):
            errors.append("every eval case must be an object")
            continue
        if case.get("behavior_only"):
            expected = case.get("expected")
            if not isinstance(expected, dict):
                errors.append(f"{case.get('id')}: behavior case requires expected")
                continue
            missing = EXPECTED_FIELDS - set(expected)
            if missing:
                errors.append(f"{case.get('id')}: missing expected fields {sorted(missing)}")
            for field in ("surface_types", "required_references", "required_states", "must_include", "must_not_include"):
                if not isinstance(expected.get(field), list):
                    errors.append(f"{case.get('id')}: expected.{field} must be a list")
        elif not all(key in case for key in ("type", "pr", "brief")):
            errors.append(f"{case.get('id')}: runnable case requires type, pr, and brief")
    rubric = read_json(RUBRIC)
    if rubric.get("schema_version") != 2:
        errors.append("evals/rubric.json must use schema_version 2")
    for field in ("hard_gates", "dimensions"):
        values = rubric.get(field)
        if not isinstance(values, list) or not values or len(values) != len(set(values)):
            errors.append(f"rubric.{field} must be a unique non-empty list")
    baseline = read_json(ROOT / "evals" / "baselines" / "v2.0.0.json")
    if baseline.get("version") != "2.0.0" or baseline.get("schema_version") != 1:
        errors.append("v2.0.0 baseline format changed unexpectedly")
    return errors


def prepare(args: argparse.Namespace) -> int:
    definition_errors = validate_definitions()
    if definition_errors:
        raise ValueError("; ".join(definition_errors))
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        raise ValueError(f"output directory is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    snapshot = output / "inputs" / "genscaff"
    shutil.copytree(CORE_SKILL, snapshot, ignore=shutil.ignore_patterns("__pycache__", "node_modules"))
    cases = [case for case in read_json(CASES)["cases"] if not case.get("behavior_only")]
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
        "reasoning": args.reasoning, "skill_snapshot_sha256": tree_digest(snapshot), "runs": runs
    })
    print(f"PREPARED_RUNS={len(runs)}")
    return 0


def stage_workspace(root: Path, item: dict, workspace: Path) -> None:
    workspace.mkdir(parents=True, exist_ok=True)
    if item["condition"] == "treatment":
        target = workspace / ".agents" / "skills" / "genscaff"
        shutil.copytree(root / "inputs" / "genscaff", target, dirs_exist_ok=True)


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
        stage_workspace(root, item, workspace)
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


def artifact_summary(run_root: Path, blind_root: Path, side: str) -> dict:
    workspace = run_root / "workspace"
    files = []
    if workspace.is_dir():
        files = sorted(str(path.relative_to(workspace)).replace("\\", "/") for path in workspace.rglob("*") if path.is_file() and ".git" not in path.parts and ".agents" not in path.parts)
    counts = collections.Counter(Path(name).suffix.lower() or "[no-extension]" for name in files)
    shots = [name for name in files if Path(name).suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}]
    anonymous_shots = []
    for index, name in enumerate(shots, start=1):
        suffix = Path(name).suffix.lower()
        target = blind_root / f"{side}-{index}{suffix}"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(workspace / name, target)
        anonymous_shots.append(str(target.relative_to(blind_root.parent.parent)).replace("\\", "/"))
    result = read_json(run_root / "result.json") if (run_root / "result.json").is_file() else {"exit_code": None}
    return {"exit_code": result.get("exit_code"), "file_type_counts": dict(sorted(counts.items())), "screenshots": anonymous_shots}


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
        blind_root = root / "blind" / "assets" / packet_id
        packets.append({
            "packet_id": packet_id,
            "left": artifact_summary(root / "runs" / ordered[0]["run_id"], blind_root, "left"),
            "right": artifact_summary(root / "runs" / ordered[1]["run_id"], blind_root, "right"),
            "human_review_required": False,
        })
        write_json(root / "private" / f"{packet_id}.json", {"left": ordered[0]["condition"], "right": ordered[1]["condition"], "pair_id": pair_id})
    review_count = max(1, (len(packets) + 4) // 5)
    for packet in sorted(packets, key=lambda value: stable_int(value["packet_id"], "human"))[:review_count]:
        packet["human_review_required"] = True
    write_json(root / "blind" / "packets.json", {"schema_version": 1, "packets": packets})
    print(f"BLIND_PACKETS={len(packets)}")
    return 0


def valid_judgment(value: dict) -> bool:
    hard = value.get("hard_gates", {})
    return (
        value.get("winner") in {"left", "right", "tie"}
        and all(isinstance(value.get("scores", {}).get(side, {}).get(dimension), int) and 0 <= value["scores"][side][dimension] <= 5 for side in ("left", "right") for dimension in DIMENSIONS)
        and all(isinstance(hard.get(side, {}).get(gate), bool) for side in ("left", "right") for gate in read_json(RUBRIC)["hard_gates"])
    )


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
        if human is not None and not valid_judgment(human):
            raise ValueError(f"invalid human judgment: {packet_id}")
        winner = human.get("winner") if human else (None if disagreement else forward["winner"])
        chosen = human if human else forward
        private = read_json(root / "private" / f"{packet_id}.json")
        by_condition = {private[side]: side for side in ("left", "right")}
        condition_winner = None if winner is None else ("tie" if winner == "tie" else private[winner])
        row = {"packet_id": packet_id, "winner": condition_winner, "judge_disagreement": disagreement, "human_adjudicated": bool(human)}
        for condition in ("control", "treatment"):
            side = by_condition[condition]
            row[condition] = {
                "hard_gate_pass": all(chosen["hard_gates"][side].values()),
                "fabricated_friction": not chosen["hard_gates"][side]["no_fabricated_friction"],
                "scores": chosen["scores"][side],
            }
        rows.append(row)
    aggregates = {}
    for condition in ("control", "treatment"):
        available = [row[condition] for row in rows]
        aggregates[condition] = {
            "hard_gate_pass_rate": sum(item["hard_gate_pass"] for item in available) / len(available) if available else None,
            "fabricated_friction_count": sum(item["fabricated_friction"] for item in available),
            "mean_scores": {dimension: (sum(item["scores"][dimension] for item in available) / len(available) if available else None) for dimension in DIMENSIONS},
        }
    write_json(root / "summary.json", {"schema_version": 1, "suite": read_json(root / "manifest.json")["suite"], "pairs_scored": len(rows), "aggregates": aggregates, "results": rows})
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
    if tree_digest(root / "inputs" / "genscaff") != manifest.get("skill_snapshot_sha256"):
        errors.append("treatment skill snapshot does not match the prepared digest")
    for item in manifest.get("runs", []):
        result_path = root / "runs" / item["run_id"] / "result.json"
        if not result_path.is_file():
            errors.append(f"missing run result: {item['run_id']}")
        elif read_json(result_path).get("exit_code") != 0:
            errors.append(f"run failed: {item['run_id']}")
    blind_path = root / "blind" / "packets.json"
    if blind_path.is_file():
        serialized = blind_path.read_text(encoding="utf-8")
        forbidden = ("control", "treatment", str(root), "workspace", "prompt.txt")
        if any(value in serialized for value in forbidden):
            errors.append("blind packet leaks condition or internal path")
        expected_pairs = expected // 2
        if len(read_json(blind_path).get("packets", [])) != expected_pairs:
            errors.append(f"expected {expected_pairs} blind packets")
    else:
        errors.append("missing blind packets")
    summary_path = root / "summary.json"
    if summary_path.is_file():
        summary = read_json(summary_path)
        packets = {packet["packet_id"]: packet for packet in read_json(blind_path)["packets"]} if blind_path.is_file() else {}
        for row in summary.get("results", []):
            if row.get("judge_disagreement") and not row.get("human_adjudicated"):
                errors.append(f"human adjudication required: {row.get('packet_id')}")
            if packets.get(row.get("packet_id"), {}).get("human_review_required") and not row.get("human_adjudicated"):
                errors.append(f"sampled human review required: {row.get('packet_id')}")
        expected_pairs = expected // 2
        if summary.get("pairs_scored") != expected_pairs:
            errors.append(f"expected {expected_pairs} scored pairs")
        treatment = summary.get("aggregates", {}).get("treatment", {})
        control = summary.get("aggregates", {}).get("control", {})
        if summary.get("suite") == "pr" and summary.get("pairs_scored") == 8:
            if treatment.get("hard_gate_pass_rate") != 1.0:
                errors.append("PR treatment contains a hard-gate failure")
        if summary.get("suite") == "release" and summary.get("pairs_scored") == 60:
            if treatment["hard_gate_pass_rate"] < 0.95:
                errors.append("treatment hard-gate pass rate is below 95%")
            if treatment["hard_gate_pass_rate"] + 0.05 < control["hard_gate_pass_rate"]:
                errors.append("treatment hard-gate pass rate trails control by more than 5 percentage points")
            if treatment["fabricated_friction_count"]:
                errors.append("treatment contains FABRICATED_FRICTION")
    else:
        errors.append("missing score summary")
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
