"""Inspect source content, selectors, resource bodies, and fingerprints."""
from __future__ import annotations

import hashlib
import base64
import re
from pathlib import Path
from typing import Any
from urllib.parse import unquote, unquote_to_bytes, urlparse
from .files import (
    iter_source_files,
    path_is_within,
    resolve_path,
)
from .hard_common import (
    DATA_URI_PATTERN,
    FORBIDDEN_SOURCE_PATTERNS,
    MAX_SOURCE_BYTES,
    get_path,
)


def decode_resource_body(
    resource: dict[str, Any], label: str, errors: list[str]
) -> bytes | None:
    body = resource.get("body")
    encoding = resource.get("encoding")
    if not isinstance(body, str):
        errors.append(f"{label} body must be a string")
        return None
    try:
        if encoding == "base64":
            decoded = base64.b64decode(body, validate=True)
        elif encoding == "utf8":
            decoded = body.encode("utf-8")
        else:
            errors.append(f"{label} body encoding must be utf8 or base64")
            return None
    except (ValueError, base64.binascii.Error):
        errors.append(f"{label} body is not valid {encoding}")
        return None
    if resource.get("body_truncated") is not True:
        if resource.get("byte_length") != len(decoded):
            errors.append(f"{label} byte length does not match its decoded body")
        if resource.get("sha256") != hashlib.sha256(decoded).hexdigest():
            errors.append(f"{label} sha256 does not match its decoded body")
    return decoded


def sniff_image_type(payload: bytes | None) -> str:
    if not payload:
        return ""
    if payload.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if payload.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if payload.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"
    if len(payload) >= 12 and payload.startswith(b"RIFF") and payload[8:12] == b"WEBP":
        return "image/webp"
    if payload.startswith(b"BM"):
        return "image/bmp"
    if len(payload) >= 12 and payload[4:8] == b"ftyp" and re.search(
        b"(?:avif|avis)", payload[8:40]
    ):
        return "image/avif"
    prefix = payload[:4096].decode("utf-8", errors="replace").lstrip("\ufeff \t\r\n")
    if re.match(r"^(?:<\?xml[^>]*>\s*)?<svg\b", prefix, re.I):
        return "image/svg+xml"
    return ""


def decoded_data_uri_payloads(content: str) -> list[str]:
    """Decode scannable text data URIs instead of trusting their surface encoding."""
    decoded: list[str] = []
    for match in DATA_URI_PATTERN.finditer(content):
        payload = match.group("payload")
        parameters = match.group("parameters").casefold()
        try:
            if ";base64" in parameters:
                raw = base64.b64decode(payload, validate=True)
            else:
                raw = unquote_to_bytes(payload)
        except (ValueError, base64.binascii.Error):
            continue
        if len(raw) > MAX_SOURCE_BYTES:
            continue
        decoded.append(raw.decode("utf-8", errors="replace"))
    return decoded


def scan_forbidden_content(content: str, label: str, errors: list[str]) -> None:
    candidates = [(content, "source")]
    try:
        percent_decoded = unquote_to_bytes(content).decode("utf-8", errors="replace")
    except (ValueError, UnicodeEncodeError):
        percent_decoded = content
    if percent_decoded != content:
        candidates.append((percent_decoded, "percent-decoded source"))
    candidates.extend((decoded, "decoded data URI") for decoded in decoded_data_uri_payloads(content))

    seen: set[str] = set()
    for candidate, provenance in candidates:
        digest = hashlib.sha256(candidate.encode("utf-8", errors="replace")).hexdigest()
        if digest in seen:
            continue
        seen.add(digest)
        for pattern_name, pattern in FORBIDDEN_SOURCE_PATTERNS:
            match = pattern.search(candidate)
            if match:
                line = candidate.count("\n", 0, match.start()) + 1
                errors.append(
                    f"Forbidden {pattern_name} pattern found in {provenance}: {label}:{line}"
                )
        if "bg-clip-text" in candidate and re.search(
            r"\b(?:from|via|to)-[^\s\"']+", candidate
        ):
            errors.append(
                f"Forbidden gradient-text utility combination found in {provenance}: {label}"
            )


def calculate_source_fingerprint(files: list[Path]) -> str:
    digest = hashlib.sha256()
    for candidate in sorted(files, key=lambda item: str(item).casefold()):
        digest.update(str(candidate).encode("utf-8"))
        digest.update(b"\0")
        digest.update(candidate.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def selector_specs(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    selectors: list[str] = []
    for item in value:
        if isinstance(item, str):
            selector = item.strip()
        elif isinstance(item, dict) and isinstance(item.get("selector"), str):
            selector = item["selector"].strip()
        else:
            selector = ""
        if selector:
            selectors.append(selector)
    return selectors


def selector_is_overbroad(selector: str) -> bool:
    compact = re.sub(r"\s+", " ", selector.strip().casefold())
    return compact in {
        "*",
        ":root",
        "html",
        "body",
        "main",
        "article",
        "section",
        "#app",
        "#root",
        "[role=main]",
        '[role="main"]',
        "body > main",
        "html > body",
    }


def validate_source_audit(
    data: dict[str, Any],
    base_dir: Path,
    errors: list[str],
    *,
    excluded_artifacts: set[Path] | None = None,
) -> tuple[list[Path], str | None]:
    audit = get_path(data, "implementation_audit")
    if not isinstance(audit, dict):
        errors.append("Missing required object: implementation_audit")
        return [], None
    roots = audit.get("source_roots")
    if not isinstance(roots, list) or not roots:
        errors.append("implementation_audit.source_roots must contain at least one project source root")
        return [], None
    rendered_roots = audit.get("rendered_roots")
    if not isinstance(rendered_roots, list) or not rendered_roots:
        errors.append(
            "implementation_audit.rendered_roots must contain the browser-served output roots"
        )
        return [], None

    project_root = resolve_path(
        audit.get("project_root"),
        base_dir,
        "implementation_audit.project_root",
        errors,
    )
    files: list[Path] = []
    if project_root is None or not project_root.is_dir():
        errors.append("implementation_audit.project_root must be an existing project directory")
    else:
        files.extend(iter_source_files(project_root))
    for index, value in enumerate(roots):
        path = f"implementation_audit.source_roots[{index}]"
        candidate = resolve_path(value, base_dir, path, errors)
        if candidate is None:
            continue
        if not candidate.exists():
            errors.append(f"Source root does not exist: {path} -> {candidate}")
            continue
        if project_root is not None and project_root.is_dir() and not path_is_within(candidate, project_root):
            errors.append(f"Source root must stay inside implementation_audit.project_root: {path}")
            continue
        files.extend(iter_source_files(candidate))

    rendered_files: list[Path] = []
    rendered_paths: list[Path] = []
    for index, value in enumerate(rendered_roots):
        path = f"implementation_audit.rendered_roots[{index}]"
        candidate = resolve_path(value, base_dir, path, errors)
        if candidate is None:
            continue
        if not candidate.exists():
            errors.append(f"Rendered root does not exist: {path} -> {candidate}")
            continue
        if project_root is not None and project_root.is_dir() and not path_is_within(candidate, project_root):
            errors.append(f"Rendered root must stay inside implementation_audit.project_root: {path}")
            continue
        rendered_paths.append(candidate)
        rendered_files.extend(iter_source_files(candidate, rendered=True))
    if not rendered_files:
        errors.append(
            "implementation_audit.rendered_roots contain no scannable browser-served files"
        )
    files.extend(rendered_files)
    if project_root is not None and project_root.is_dir():
        for directory_name in ("dist", "build", "out", ".next", ".nuxt", ".output", ".svelte-kit"):
            generated_root = (project_root / directory_name).resolve()
            if not generated_root.is_dir() or not iter_source_files(generated_root, rendered=True):
                continue
            covered = False
            for rendered_path in rendered_paths:
                if not rendered_path.is_dir():
                    continue
                try:
                    generated_root.relative_to(rendered_path)
                    covered = True
                    break
                except ValueError:
                    continue
            if not covered:
                errors.append(
                    f"Generated browser output must be included in implementation_audit.rendered_roots: {generated_root}"
                )

    excluded = {item.resolve() for item in (excluded_artifacts or set())}
    files = sorted(
        {item for item in files if item.resolve() not in excluded},
        key=lambda item: str(item).casefold(),
    )
    if not files:
        errors.append("implementation_audit.source_roots contain no scannable frontend source files")
        return [], None

    for candidate in files:
        size = candidate.stat().st_size
        if size > MAX_SOURCE_BYTES:
            errors.append(f"Source file is too large for deterministic scan: {candidate} ({size} bytes)")
            continue
        try:
            content = candidate.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            errors.append(f"Unable to read source file {candidate}: {exc}")
            continue
        scan_forbidden_content(content, str(candidate), errors)

    fingerprint = calculate_source_fingerprint(files)
    reported = audit.get("source_fingerprint")
    if reported != fingerprint:
        errors.append(
            "implementation_audit.source_fingerprint does not match the scanned source tree; "
            f"expected {fingerprint}"
        )
    return files, fingerprint
