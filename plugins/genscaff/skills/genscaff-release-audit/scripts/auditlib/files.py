"""Resolve bounded artifact paths and enumerate source files."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import unquote, unquote_to_bytes, urlparse
from .hard_common import (
    IGNORED_DIRECTORIES,
    RENDERED_IGNORED_DIRECTORIES,
    RENDERED_SOURCE_SUFFIXES,
    SOURCE_SUFFIXES,
)


def resolve_path(value: Any, base_dir: Path, path: str, errors: list[str]) -> Path | None:
    if not isinstance(value, str) or len(value.strip()) < 3:
        errors.append(f"Missing local file path: {path}")
        return None
    if value.startswith(("http://", "https://")):
        errors.append(f"Remote file cannot satisfy a hard gate: {path}")
        return None
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        candidate = base_dir / candidate
    try:
        return candidate.resolve()
    except OSError as exc:
        errors.append(f"Unable to resolve {path}: {exc}")
        return None


def path_is_within(candidate: Path, root: Path) -> bool:
    try:
        candidate.resolve().relative_to(root.resolve())
        return True
    except (OSError, ValueError):
        return False


def file_url_path(value: Any, base_dir: Path | None = None) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    parsed = urlparse(value)
    if parsed.scheme not in {"", "file"}:
        return None
    if parsed.scheme == "file":
        raw_path = unquote(parsed.path)
        if re.match(r"^/[A-Za-z]:/", raw_path):
            raw_path = raw_path[1:]
        candidate = Path(raw_path)
    else:
        candidate = Path(value)
        if not candidate.is_absolute() and base_dir is not None:
            candidate = base_dir / candidate
    try:
        return candidate.resolve()
    except OSError:
        return None


def canonical_project_index(project_root: Path, errors: list[str]) -> Path | None:
    """Choose the project entry without allowing a deeper audit-only index to win."""
    candidates = sorted(
        {
            item.resolve()
            for item in iter_source_files(project_root, rendered=True)
            if item.name.casefold() in {"index.html", "index.htm"}
        },
        key=lambda item: str(item).casefold(),
    )
    if not candidates:
        return None
    direct = [item for item in candidates if item.parent == project_root.resolve()]
    if len(direct) > 1:
        errors.append(
            "implementation_audit.project_root has ambiguous top-level index.html/index.htm entries"
        )
        return None
    if direct:
        return direct[0]
    depths = {
        item: len(item.relative_to(project_root.resolve()).parts)
        for item in candidates
    }
    minimum_depth = min(depths.values())
    shallowest = [item for item, depth in depths.items() if depth == minimum_depth]
    if len(shallowest) != 1:
        errors.append(
            "implementation_audit.project_root has multiple equally plausible browser index entries; "
            "narrow project_root to the audited deliverable"
        )
        return None
    return shallowest[0]


def load_json_file(value: Any, base_dir: Path, path: str, errors: list[str]) -> tuple[dict[str, Any] | None, Path | None]:
    candidate = resolve_path(value, base_dir, path, errors)
    if candidate is None:
        return None, None
    if not candidate.is_file() or candidate.suffix.casefold() != ".json":
        errors.append(f"Hard-gate artifact must be an existing JSON file: {path} -> {candidate}")
        return None, candidate
    try:
        parsed = json.loads(candidate.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"Unable to parse hard-gate JSON at {path}: {exc}")
        return None, candidate
    if not isinstance(parsed, dict):
        errors.append(f"Hard-gate JSON root must be an object: {path}")
        return None, candidate
    return parsed, candidate


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def iter_source_files(root: Path, *, rendered: bool = False) -> list[Path]:
    suffixes = RENDERED_SOURCE_SUFFIXES if rendered else SOURCE_SUFFIXES
    if root.is_file():
        return [root] if root.suffix.casefold() in suffixes else []
    found: list[Path] = []
    ignored = RENDERED_IGNORED_DIRECTORIES if rendered else IGNORED_DIRECTORIES
    for candidate in root.rglob("*"):
        if not candidate.is_file() or candidate.suffix.casefold() not in suffixes:
            continue
        relative_parts = candidate.relative_to(root).parts[:-1]
        if any(part.casefold() in ignored for part in relative_parts):
            continue
        found.append(candidate.resolve())
    return found
