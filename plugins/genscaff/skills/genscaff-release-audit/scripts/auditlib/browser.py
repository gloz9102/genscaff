"""Run browser and Lighthouse audits under the existing approval boundary."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any
from urllib.parse import unquote, unquote_to_bytes, urlparse
from .files import (
    canonical_project_index,
    load_json_file,
    path_is_within,
    resolve_path,
)
from .hard_common import (
    get_path,
)


def run_live_audit(
    data: dict[str, Any],
    base_dir: Path,
    source_fingerprint: str | None,
    errors: list[str],
    bundle_override: dict[str, Any] | None = None,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, Path | None]:
    config, config_path = load_json_file(
        get_path(data, "implementation_audit.live_audit_config"),
        base_dir,
        "implementation_audit.live_audit_config",
        errors,
    )
    if config is None or config_path is None:
        return None, config, config_path
    if config.get("schema_version") != 1:
        errors.append("live_audit_config.schema_version must be 1")
    if source_fingerprint and config.get("source_fingerprint") != source_fingerprint:
        errors.append("live_audit_config.source_fingerprint does not match the scanned source tree")
    if config.get("allow_non_default_route") is True:
        errors.append("live_audit_config.allow_non_default_route cannot bypass default-route evidence")
    project_root = resolve_path(
        get_path(data, "implementation_audit.project_root"),
        base_dir,
        "implementation_audit.project_root",
        errors,
    )
    canonical_entry = (
        canonical_project_index(project_root, errors)
        if project_root is not None and project_root.is_dir()
        else None
    )
    raw_entry = config.get("entry_url")
    parsed_entry = urlparse(raw_entry) if isinstance(raw_entry, str) else None
    if parsed_entry is None:
        errors.append("live_audit_config.entry_url is required")
    elif parsed_entry.scheme in {"http", "https"}:
        if parsed_entry.username or parsed_entry.password:
            errors.append("live_audit_config.entry_url cannot contain credentials")
        if parsed_entry.path not in {"", "/"} or parsed_entry.query or parsed_entry.fragment:
            errors.append(
                "live_audit_config.entry_url must request the origin root; let the application perform any canonical redirect"
            )
    elif parsed_entry.scheme in {"", "file"}:
        if parsed_entry.scheme == "file":
            raw_path = unquote(parsed_entry.path)
            if re.match(r"^/[A-Za-z]:/", raw_path):
                raw_path = raw_path[1:]
            entry_path = Path(raw_path)
        else:
            entry_path = Path(str(raw_entry))
            if not entry_path.is_absolute():
                entry_path = config_path.parent / entry_path
        try:
            entry_path = entry_path.resolve()
        except OSError:
            entry_path = Path()
        if not entry_path.is_file() or entry_path.name.casefold() not in {"index.html", "index.htm"}:
            errors.append(
                "File-based live_audit_config.entry_url must be an existing rendered-root index.html"
            )
        if project_root is None or not project_root.is_dir() or not path_is_within(entry_path, project_root):
            errors.append(
                "File-based live_audit_config.entry_url must stay inside implementation_audit.project_root"
            )
        if canonical_entry is None:
            errors.append(
                "File-based live_audit_config.entry_url requires one unambiguous canonical project index"
            )
        elif entry_path != canonical_entry:
            errors.append(
                "File-based live_audit_config.entry_url must use the canonical project index; "
                f"expected {canonical_entry}"
            )
        rendered_values = get_path(data, "implementation_audit.rendered_roots", [])
        at_rendered_root = False
        for value in rendered_values if isinstance(rendered_values, list) else []:
            rendered = resolve_path(value, base_dir, "implementation_audit.rendered_roots", errors)
            if rendered is None:
                continue
            if rendered.is_file() and rendered == entry_path:
                at_rendered_root = True
                break
            if rendered.is_dir() and entry_path.parent == rendered:
                at_rendered_root = True
                break
        if not at_rendered_root:
            errors.append(
                "File-based live_audit_config.entry_url must be the direct index of a declared rendered_root"
            )
    else:
        errors.append("live_audit_config.entry_url must use file, http, or https")
    output_dir = resolve_path(
        config.get("output_dir"),
        config_path.parent,
        "live_audit_config.output_dir",
        errors,
    )
    if output_dir is None:
        errors.append("live_audit_config.output_dir is required for gate-owned screenshots")

    # Test-only injection point. The public CLI never supplies this value; production
    # validation always launches the bundled runner below.
    if bundle_override is not None:
        return bundle_override, config, config_path

    runner = Path(__file__).resolve().parent.parent / "live_audit.js"
    if not runner.is_file():
        errors.append(f"Gate-owned live browser runner is missing: {runner}")
        return None, config, config_path
    try:
        completed = subprocess.run(
            ["node", str(runner), "--config", str(config_path)],
            cwd=str(config_path.parent),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
            check=False,
        )
    except FileNotFoundError:
        errors.append("Node.js is required for the gate-owned live browser audit")
        return None, config, config_path
    except subprocess.TimeoutExpired:
        errors.append("Gate-owned live browser audit exceeded the 120 second hard timeout")
        return None, config, config_path
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()[-1200:]
        errors.append(f"Gate-owned live browser audit failed: {detail}")
        return None, config, config_path
    try:
        bundle = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        errors.append(f"Gate-owned live browser audit returned invalid JSON: {exc}")
        return None, config, config_path
    if not isinstance(bundle, dict):
        errors.append("Gate-owned live browser audit output must be an object")
        return None, config, config_path
    return bundle, config, config_path


def run_lighthouse_audit(
    config_path: Path | None,
    errors: list[str],
    bundle_override: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    if config_path is None:
        return None
    if bundle_override is not None:
        return bundle_override
    runner = Path(__file__).resolve().parent.parent / "lighthouse_audit.js"
    if not runner.is_file():
        errors.append(f"Gate-owned Lighthouse runner is missing: {runner}")
        return None
    try:
        completed = subprocess.run(
            ["node", str(runner), "--config", str(config_path)],
            cwd=str(config_path.parent),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=240,
            check=False,
        )
    except FileNotFoundError:
        errors.append("Node.js is required for the gate-owned Lighthouse audit")
        return None
    except subprocess.TimeoutExpired:
        errors.append("Gate-owned Lighthouse audit exceeded the 240 second hard timeout")
        return None
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()[-1200:]
        errors.append(f"Gate-owned Lighthouse audit failed: {detail}")
        return None
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        errors.append(f"Gate-owned Lighthouse audit returned invalid JSON: {exc}")
        return None
    if not isinstance(result, dict):
        errors.append("Gate-owned Lighthouse audit output must be an object")
        return None
    return result
