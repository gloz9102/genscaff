"""Validate and replay explicitly approved repository commands."""
from __future__ import annotations

import re
import shlex
import subprocess
from pathlib import Path
from typing import Any
from .files import (
    file_sha256,
    load_json_file,
    resolve_path,
)
from .hard_common import (
    COMMAND_RESULT_CACHE,
    EXECUTION_GENERATOR,
    get_path,
    parse_timestamp,
    require_manifest_header,
)


def safe_verification_argv(command: str, cwd: Path, errors: list[str], path: str) -> list[str] | None:
    if re.search(r"[;&|<>`\r\n]|\$\(", command):
        errors.append(f"{path}.command contains forbidden shell syntax")
        return None
    try:
        argv = shlex.split(command, posix=False)
    except ValueError as exc:
        errors.append(f"{path}.command cannot be parsed safely: {exc}")
        return None
    if not argv:
        errors.append(f"{path}.command is empty")
        return None
    argv = [
        item[1:-1] if len(item) >= 2 and item[0] == item[-1] and item[0] in {"'", '"'} else item
        for item in argv
    ]
    executable = Path(argv[0]).name.casefold()
    package_runners = {"npm", "npm.cmd", "pnpm", "pnpm.cmd", "yarn", "yarn.cmd", "bun", "bun.exe"}
    direct_tools = {"pytest", "pytest.exe", "ruff", "ruff.exe", "cargo", "cargo.exe", "dotnet", "dotnet.exe"}
    if executable in package_runners:
        package_script_ok = (
            len(argv) >= 3
            and argv[1] == "run"
            and bool(re.fullmatch(r"[\w:.-]+", argv[2]))
        ) or (
            len(argv) >= 2
            and argv[1] in {"build", "check", "lint", "test", "typecheck"}
        )
        if not package_script_ok:
            errors.append(f"{path}.command must invoke a named package verification script")
            return None
    elif executable in {"node", "node.exe"}:
        if len(argv) != 2 or not re.fullmatch(r"[\w./\\ -]+\.(?:c?js|mjs)", argv[1], flags=re.IGNORECASE):
            errors.append(f"{path}.command may run only one repository-local JS verification script")
            return None
        script = (cwd / argv[1]).resolve() if not Path(argv[1]).is_absolute() else Path(argv[1]).resolve()
        try:
            script.relative_to(cwd)
        except ValueError:
            errors.append(f"{path}.command JS script must stay inside its declared cwd")
            return None
        if not script.is_file():
            errors.append(f"{path}.command JS script does not exist: {script}")
            return None
        argv[1] = str(script)
    elif executable in {"python", "python.exe", "python3", "python3.exe"}:
        if len(argv) < 3 or argv[1:3] not in (["-m", "pytest"], ["-m", "ruff"]):
            errors.append(f"{path}.command Python execution is limited to -m pytest or -m ruff")
            return None
    elif executable not in direct_tools:
        errors.append(f"{path}.command executable is outside the verification allowlist: {argv[0]}")
        return None
    return argv


def execute_verification_command(
    command: str,
    cwd: Path,
    source_fingerprint: str | None,
    path: str,
    errors: list[str],
) -> tuple[int, str] | None:
    argv = safe_verification_argv(command, cwd, errors, path)
    if argv is None:
        return None
    cache_key = (str(cwd), command, source_fingerprint or "")
    if cache_key in COMMAND_RESULT_CACHE:
        return COMMAND_RESULT_CACHE[cache_key]
    try:
        completed = subprocess.run(
            argv,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
            check=False,
        )
    except FileNotFoundError:
        errors.append(f"{path}.command executable was not found: {argv[0]}")
        return None
    except subprocess.TimeoutExpired:
        errors.append(f"{path}.command exceeded the 180 second hard timeout")
        return None
    output = (completed.stdout + "\n" + completed.stderr).strip()
    result = (completed.returncode, output)
    if len(COMMAND_RESULT_CACHE) >= 64:
        COMMAND_RESULT_CACHE.pop(next(iter(COMMAND_RESULT_CACHE)))
    COMMAND_RESULT_CACHE[cache_key] = result
    return result


def validate_execution_manifest(
    data: dict[str, Any],
    base_dir: Path,
    source_fingerprint: str | None,
    errors: list[str],
    *,
    execute_approved_commands: bool = False,
) -> None:
    manifest, manifest_path = load_json_file(
        get_path(data, "measurements.execution_manifest"),
        base_dir,
        "measurements.execution_manifest",
        errors,
    )
    if manifest is None or manifest_path is None:
        return
    require_manifest_header(manifest, EXECUTION_GENERATOR, "execution_manifest", errors)
    if source_fingerprint and manifest.get("source_fingerprint") != source_fingerprint:
        errors.append("execution_manifest.source_fingerprint does not match the scanned source tree")
    runs = manifest.get("runs")
    if not isinstance(runs, list) or not runs:
        errors.append("execution_manifest.runs must contain actual command records")
        return
    project_root = resolve_path(
        get_path(data, "implementation_audit.project_root"),
        base_dir,
        "implementation_audit.project_root",
        errors,
    )
    run_commands: set[str] = set()
    for index, run in enumerate(runs):
        path = f"execution_manifest.runs[{index}]"
        if not isinstance(run, dict):
            errors.append(f"Command run must be an object: {path}")
            continue
        command = run.get("command")
        if not isinstance(command, str) or len(command.strip()) < 4:
            errors.append(f"{path}.command is required")
            continue
        run_commands.add(command.strip())
        started = parse_timestamp(run.get("started_at"), f"{path}.started_at", errors)
        finished = parse_timestamp(run.get("finished_at"), f"{path}.finished_at", errors)
        if started is not None and finished is not None and finished <= started:
            errors.append(f"{path} must finish after it starts")
        if run.get("exit_code") != 0:
            errors.append(f"{path}.exit_code must be 0")
        if not isinstance(run.get("cwd"), str) or len(run["cwd"].strip()) < 3:
            errors.append(f"{path}.cwd is required")
            cwd = None
        else:
            cwd = resolve_path(run.get("cwd"), manifest_path.parent, f"{path}.cwd", errors)
            if cwd is None or not cwd.is_dir():
                errors.append(f"{path}.cwd must be an existing directory")
                cwd = None
            elif project_root is not None:
                try:
                    cwd.relative_to(project_root)
                except ValueError:
                    errors.append(f"{path}.cwd must stay inside implementation_audit.project_root")
                    cwd = None
        log_path = resolve_path(run.get("log"), manifest_path.parent, f"{path}.log", errors)
        if log_path is None or not log_path.is_file() or log_path.stat().st_size < 20:
            errors.append(f"{path}.log must be a non-trivial local command log")
        elif run.get("log_sha256") != file_sha256(log_path):
            errors.append(f"{path}.log_sha256 does not match the command log")
        if cwd is not None and execute_approved_commands:
            observed = execute_verification_command(
                command.strip(), cwd, source_fingerprint, path, errors
            )
            if observed is not None:
                observed_code, observed_output = observed
                if observed_code != 0:
                    errors.append(
                        f"{path}.command failed during validator-owned re-execution with exit code {observed_code}: "
                        f"{observed_output[-600:]}"
                    )
                if observed_code != run.get("exit_code"):
                    errors.append(f"{path}.exit_code does not match validator-owned re-execution")
    report_commands = {
        item.get("command", "").strip()
        for item in get_path(data, "measurements.commands", [])
        if isinstance(item, dict) and isinstance(item.get("command"), str)
    }
    if run_commands != report_commands:
        errors.append("execution_manifest commands must match measurements.commands exactly")
