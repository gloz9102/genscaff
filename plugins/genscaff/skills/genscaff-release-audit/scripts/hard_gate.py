#!/usr/bin/env python3
"""Evidence-backed, non-compensating gates for Genscaff Strict reports."""

from __future__ import annotations

import hashlib
import json
import base64
import re
import shlex
import struct
import subprocess
import zlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import unquote, unquote_to_bytes, urlparse


MANIFEST_SCHEMA_VERSION = 1
CAPTURE_GENERATOR = "genscaff-browser-capture-v1"
STYLE_GENERATOR = "genscaff-computed-style-audit-v1"
CONTROL_GENERATOR = "genscaff-control-audit-v1"
REVIEW_GENERATOR = "genscaff-independent-review-v1"
EXECUTION_GENERATOR = "genscaff-command-runner-v1"
CONTENT_GENERATOR = "genscaff-content-audit-v1"

SOURCE_SUFFIXES = {
    ".astro",
    ".cjs",
    ".css",
    ".htm",
    ".html",
    ".js",
    ".jsx",
    ".less",
    ".mjs",
    ".pcss",
    ".sass",
    ".scss",
    ".svelte",
    ".svg",
    ".ts",
    ".tsx",
    ".vue",
}
RENDERED_SOURCE_SUFFIXES = SOURCE_SUFFIXES | {".json", ".xml"}
IGNORED_DIRECTORIES = {
    ".git",
    ".next",
    ".nuxt",
    ".output",
    ".svelte-kit",
    ".turbo",
    "coverage",
    "node_modules",
    "vendor",
}
RENDERED_IGNORED_DIRECTORIES = {
    ".git",
    "coverage",
    "node_modules",
    "vendor",
}
MAX_SOURCE_BYTES = 5_000_000
MAX_IMAGE_PIXELS = 20_000_000
BROWSER_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif"}
PNG_DECODE_CACHE: dict[str, dict[str, Any]] = {}
COMMAND_RESULT_CACHE: dict[tuple[str, str, str], tuple[int, str]] = {}

FORBIDDEN_SOURCE_PATTERNS = (
    (
        "gradient-function",
        re.compile(
            r"(?i)(?:repeating-)?(?:linear|radial|conic)-gradient\s*\(|"
            r"create(?:linear|radial|conic)gradient\s*\("
        ),
    ),
    ("svg-gradient", re.compile(r"(?i)<\s*(?:linear|radial)gradient\b")),
    (
        "backdrop-filter",
        re.compile(
            r"(?i)(?:-webkit-)?backdrop-filter\s*[\"']?\s*:|"
            r"\b(?:webkit)?backdropFilter\s*[\"']?\s*[:=]"
        ),
    ),
    (
        "tailwind-gradient-or-glass",
        re.compile(
            r"(?i)\b(?:bg-gradient-to-[^\s\"']+|bg-\[(?:linear|radial|conic)-gradient"
            r"|backdrop-blur(?:-[^\s\"']+)?)"
        ),
    ),
    ("svg-blur", re.compile(r"(?i)<\s*feGaussianBlur\b")),
    ("css-blur", re.compile(r"(?i)(?<!backdrop-)filter\s*:\s*blur\s*\(")),
)

DATA_URI_PATTERN = re.compile(
    r"data:(?P<mime>image/svg\+xml|text/css|text/html|application/(?:javascript|json))"
    r"(?P<parameters>(?:;[^,\s\"']*)*),(?P<payload>[^\s\"'<>]+)",
    flags=re.IGNORECASE,
)

COSMETIC_TERMS = {
    "accent",
    "blue",
    "brand",
    "color",
    "colour",
    "font",
    "gradient",
    "icon",
    "logo",
    "palette",
    "purple",
    "style",
    "typography",
    "visual",
}
GENERIC_CTA_PATTERNS = (
    re.compile(r"^(?:learn\s+more|get\s+started|explore|discover|continue|submit|start|begin)\b"),
    re.compile(r"^(?:자세히\s*보기|더\s*알아보기|시작하기|둘러보기|계속|제출)(?:\s|$)"),
)
SUBSTITUTION_AXES = (
    "information_architecture",
    "data_schema",
    "state_transitions",
    "action_sequence",
    "failure_recovery",
)
STYLE_EMPTY_FIELDS = (
    "gradient_matches",
    "backdrop_blur_matches",
    "glass_surface_matches",
    "blur_or_glow_matches",
    "svg_gradient_or_blur_matches",
    "raster_visual_findings",
)
STOPWORDS = {
    "and",
    "app",
    "application",
    "dashboard",
    "for",
    "platform",
    "product",
    "service",
    "system",
    "the",
    "tool",
    "user",
    "workspace",
}


def get_path(data: dict[str, Any], path: str, default: Any = None) -> Any:
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return default
        current = current[part]
    return current


def normalized(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(re.findall(r"[\w가-힣]+", value.casefold(), flags=re.UNICODE))


def meaningful_tokens(value: Any) -> set[str]:
    if not isinstance(value, str):
        return set()
    tokens: set[str] = set()
    for raw_token in re.findall(r"[\w가-힣]+", value, flags=re.UNICODE):
        token = raw_token.casefold()
        is_acronym = 2 <= len(raw_token) <= 6 and raw_token.isupper()
        if (len(token) < 4 and not is_acronym) or token in STOPWORDS:
            continue
        if token.endswith("ies") and len(token) > 5:
            token = token[:-3] + "y"
        elif token.endswith("es") and len(token) > 5:
            token = token[:-2]
        elif token.endswith("s") and len(token) > 4:
            token = token[:-1]
        tokens.add(token)
    return tokens


def live_signal_is_substantive(match: dict[str, Any]) -> bool:
    numeric_minimums = {
        "width": 40,
        "height": 14,
        "font_size": 11,
        "opacity": 0.85,
        "effective_opacity": 0.85,
        "visible_text_rect_count": 1,
        "visible_text_pixel_area": 80,
        "unoccluded_text_ratio": 0.6,
        "minimum_text_color_alpha": 0.5,
    }
    for field, minimum in numeric_minimums.items():
        value = match.get(field)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value < minimum:
            return False
    return (
        match.get("visible") is True
        and match.get("intersects_viewport") is True
        and match.get("aria_hidden") is False
        and match.get("clipped") is False
    )


def parse_timestamp(value: Any, path: str, errors: list[str]) -> float | None:
    if not isinstance(value, str) or len(value.strip()) < 20:
        errors.append(f"Missing or invalid timestamp: {path}")
        return None
    candidate = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        errors.append(f"Timestamp must be ISO-8601: {path}")
        return None
    if parsed.tzinfo is None:
        errors.append(f"Timestamp must include a timezone: {path}")
        return None
    timestamp = parsed.astimezone(timezone.utc).timestamp()
    if timestamp > datetime.now(timezone.utc).timestamp() + 300:
        errors.append(f"Timestamp cannot be in the future: {path}")
        return None
    return timestamp


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


def require_manifest_header(
    manifest: dict[str, Any], generator: str, path: str, errors: list[str]
) -> None:
    if manifest.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        errors.append(f"{path}.schema_version must be {MANIFEST_SCHEMA_VERSION}")
    if manifest.get("generated_by") != generator:
        errors.append(f"{path}.generated_by must be {generator!r}")


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

    runner = Path(__file__).resolve().with_name("live_audit.js")
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
    runner = Path(__file__).resolve().with_name("lighthouse_audit.js")
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


def live_control_key(control: Any) -> tuple[str, str] | None:
    if not isinstance(control, dict):
        return None
    selector = control.get("selector")
    name = control.get("accessible_name") or control.get("label")
    if not isinstance(selector, str) or not isinstance(name, str):
        return None
    selector = selector.strip()
    name = normalized(name)
    if not selector or not name:
        return None
    return selector, name


def validate_live_audit_bundle(
    bundle: dict[str, Any] | None,
    config: dict[str, Any] | None,
    config_path: Path | None,
    data: dict[str, Any],
    base_dir: Path,
    source_fingerprint: str | None,
    captures: dict[Path, dict[str, Any]],
    errors: list[str],
) -> None:
    if bundle is None or config is None or config_path is None:
        return
    expected_file_entry = file_url_path(config.get("entry_url"), config_path.parent)
    expected_file_url = expected_file_entry.as_uri() if expected_file_entry is not None else None
    if bundle.get("schema_version") != 1 or bundle.get("generated_by") != "genscaff-live-audit-v1":
        errors.append("Live audit bundle has an invalid schema or generator")
    if not re.fullmatch(
        r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}",
        str(bundle.get("run_id", "")),
    ):
        errors.append("Live audit bundle.run_id must be a UUID generated by the runner")
    started = parse_timestamp(bundle.get("started_at"), "live_audit.started_at", errors)
    completed = parse_timestamp(bundle.get("completed_at"), "live_audit.completed_at", errors)
    if started is not None and completed is not None and completed <= started:
        errors.append("Live audit completed_at must be after started_at")
    if source_fingerprint and bundle.get("source_fingerprint") != source_fingerprint:
        errors.append("Live audit bundle source_fingerprint does not match the scanned source tree")

    expected_runner = Path(__file__).resolve().with_name("live_audit.js")
    runner_info = bundle.get("runner")
    if not isinstance(runner_info, dict):
        errors.append("Live audit bundle is missing runner provenance")
    else:
        try:
            actual_runner = Path(str(runner_info.get("path", ""))).resolve()
        except OSError:
            actual_runner = Path()
        if actual_runner != expected_runner:
            errors.append("Live audit must be produced by the bundled gate-owned runner")
        if runner_info.get("sha256") != file_sha256(expected_runner):
            errors.append("Live audit runner sha256 does not match the bundled runner")
    config_info = bundle.get("config")
    if not isinstance(config_info, dict):
        errors.append("Live audit bundle is missing config provenance")
    else:
        try:
            actual_config = Path(str(config_info.get("path", ""))).resolve()
        except OSError:
            actual_config = Path()
        if actual_config != config_path.resolve():
            errors.append("Live audit config path does not match implementation_audit.live_audit_config")
        if config_info.get("sha256") != file_sha256(config_path):
            errors.append("Live audit config sha256 does not match the executed config")
    browser = bundle.get("browser")
    if not isinstance(browser, dict) or browser.get("engine") != "chromium":
        errors.append("Live audit must use a fresh Chromium browser context")
    elif not isinstance(browser.get("version"), str) or not re.match(r"^\d+\.", browser["version"]):
        errors.append("Live audit bundle is missing a Chromium version")

    counts = bundle.get("prohibited_finding_counts")
    required_count_fields = {
        "computed_style",
        "svg",
        "canvas_gradient",
        "data_uri",
        "loaded_resource",
    }
    if not isinstance(counts, dict) or set(counts) != required_count_fields:
        errors.append("Live audit prohibited_finding_counts is incomplete")
    else:
        for field in sorted(required_count_fields):
            if counts.get(field) != 0:
                errors.append(f"Live audit found prohibited {field} output: {counts.get(field)}")

    report_signal_selectors = [
        item.get("selector", "").strip()
        for item in get_path(data, "product_specificity.domain_signals", [])
        if isinstance(item, dict) and isinstance(item.get("selector"), str)
    ]
    report_decision_selectors = [
        item.get("selector", "").strip()
        for item in get_path(data, "product_specificity.decision_points", [])
        if isinstance(item, dict) and isinstance(item.get("selector"), str)
    ]
    config_signal_selectors = selector_specs(config.get("domain_signal_selectors"))
    config_decision_selectors = selector_specs(config.get("decision_selectors"))
    if len(report_signal_selectors) != len(set(report_signal_selectors)):
        errors.append("product_specificity.domain_signals selectors must be unique")
    if len(report_decision_selectors) != len(set(report_decision_selectors)):
        errors.append("product_specificity.decision_points selectors must be unique")
    if set(report_signal_selectors) & set(report_decision_selectors):
        errors.append("Domain and decision evidence must use distinct selectors")
    if len(config_signal_selectors) != len(set(config_signal_selectors)):
        errors.append("live_audit_config.domain_signal_selectors must be unique")
    if len(config_decision_selectors) != len(set(config_decision_selectors)):
        errors.append("live_audit_config.decision_selectors must be unique")
    for selector in report_signal_selectors + report_decision_selectors:
        if selector_is_overbroad(selector):
            errors.append(f"Product evidence selector is an overbroad application container: {selector}")
    if set(config_signal_selectors) != set(report_signal_selectors) or len(config_signal_selectors) != len(report_signal_selectors):
        errors.append("live_audit_config domain selectors must exactly match report domain signals")
    if set(config_decision_selectors) != set(report_decision_selectors) or len(config_decision_selectors) != len(report_decision_selectors):
        errors.append("live_audit_config decision selectors must exactly match report decision points")

    report_controls = get_path(data, "action_trace.control_inventory", [])
    report_control_keys: set[tuple[str, str]] = set()
    report_by_selector: dict[str, dict[str, Any]] = {}
    for index, control in enumerate(report_controls if isinstance(report_controls, list) else []):
        key = live_control_key(control)
        if key is None:
            errors.append(
                f"action_trace.control_inventory[{index}] needs a selector and accessible_name for live cross-checking"
            )
            continue
        if key in report_control_keys or key[0] in report_by_selector:
            errors.append(f"Duplicate live control identity in action_trace.control_inventory[{index}]")
        report_control_keys.add(key)
        report_by_selector[key[0]] = control

    raw_config_scenarios = config.get("control_scenarios")
    config_scenarios: dict[str, dict[str, Any]] = {}
    if not isinstance(raw_config_scenarios, list):
        errors.append("live_audit_config.control_scenarios must be a list")
        raw_config_scenarios = []
    for index, scenario in enumerate(raw_config_scenarios):
        path = f"live_audit_config.control_scenarios[{index}]"
        if not isinstance(scenario, dict):
            errors.append(f"{path} must be an object")
            continue
        selector = scenario.get("selector")
        if not isinstance(selector, str) or not selector.strip():
            errors.append(f"{path}.selector is required")
            continue
        selector = selector.strip()
        if selector in config_scenarios:
            errors.append(f"{path}.selector is duplicated: {selector}")
        config_scenarios[selector] = scenario
        action = scenario.get("action", "click")
        if action not in {"click", "fill", "select", "check", "press"}:
            errors.append(f"{path}.action is unsupported")
        if action in {"fill", "select"} and not isinstance(scenario.get("value"), str):
            errors.append(f"{path}.value is required for {action}")
        if action == "press" and not isinstance(scenario.get("key"), str):
            errors.append(f"{path}.key is required for press")
        setup = scenario.get("setup", "default")
        if setup not in {"default", "primary-feedback", "primary-terminal"}:
            errors.append(f"{path}.setup is invalid")
        for field in ("expected_selector", "expected_url_pattern", "expected_value"):
            if field in scenario and not isinstance(scenario.get(field), str):
                errors.append(f"{path}.{field} must be a string")
        if "expected_checked" in scenario and not isinstance(scenario.get("expected_checked"), bool):
            errors.append(f"{path}.expected_checked must be boolean")
        if not any(
            field in scenario
            for field in ("expected_selector", "expected_url_pattern", "expected_value", "expected_checked")
        ):
            errors.append(f"{path} needs an observable expected outcome")
        pattern = scenario.get("expected_url_pattern")
        if isinstance(pattern, str):
            try:
                re.compile(pattern)
            except re.error as exc:
                errors.append(f"{path}.expected_url_pattern is invalid: {exc}")

    primary_selector = get_path(config, "primary_flow.selector")
    recovery_selector = get_path(config, "primary_flow.recovery_selector")
    disabled_selectors = {
        selector
        for selector, control in report_by_selector.items()
        if control.get("behavior") == "disabled"
    }
    primary_report = [
        control
        for control in report_by_selector.values()
        if control.get("role") == "primary"
    ]
    if len(primary_report) != 1 or primary_report[0].get("selector") != primary_selector:
        errors.append("Live primary selector must identify the report's sole primary control")
    if recovery_selector not in report_by_selector:
        errors.append("Live recovery selector must be present in action_trace.control_inventory")
    elif report_by_selector[recovery_selector].get("behavior") == "disabled":
        errors.append("Live recovery selector cannot be declared disabled")
    if primary_selector in disabled_selectors:
        errors.append("Live primary selector cannot be declared disabled")

    content_manifest, _ = load_json_file(
        get_path(data, "implementation_audit.content_manifest"),
        base_dir,
        "implementation_audit.content_manifest",
        errors,
    )
    manifest_claims: set[tuple[str, str]] = set()
    if isinstance(content_manifest, dict):
        for item in content_manifest.get("visible_claims", []):
            if isinstance(item, dict) and isinstance(item.get("selector"), str):
                manifest_claims.add((item["selector"].strip(), normalized(item.get("text"))))

    captures_by_checkpoint: dict[tuple[str, str], dict[str, Any]] = {}
    for record in captures.values():
        key = (str(record.get("viewport", "")), str(record.get("checkpoint", "")))
        if key in captures_by_checkpoint:
            errors.append(f"Capture manifest repeats live checkpoint {key}")
        captures_by_checkpoint[key] = record

    viewports = bundle.get("viewports")
    if not isinstance(viewports, list):
        errors.append("Live audit bundle.viewports must be a list")
        return
    viewport_names = [item.get("name") for item in viewports if isinstance(item, dict)]
    if set(viewport_names) != {"desktop", "mobile"} or len(viewport_names) != 2:
        errors.append("Live audit must contain exactly one desktop and one mobile viewport")

    all_live_claims: set[tuple[str, str]] = set()
    for viewport in viewports:
        if not isinstance(viewport, dict):
            errors.append("Live audit viewport must be an object")
            continue
        name = viewport.get("name")
        width = viewport.get("width")
        if expected_file_url is not None and viewport.get("default_route_url") != expected_file_url:
            errors.append(f"Live {name} default route does not match the canonical file entry")
        if name == "desktop" and (isinstance(width, bool) or not isinstance(width, int) or width < 1024):
            errors.append("Live desktop viewport must be at least 1024 CSS pixels wide")
        if name == "mobile" and (isinstance(width, bool) or not isinstance(width, int) or not 320 <= width <= 480):
            errors.append("Live mobile viewport must be between 320 and 480 CSS pixels wide")
        for category, values in (viewport.get("errors") or {}).items():
            if not isinstance(values, list) or values:
                errors.append(f"Live {name} browser {category} errors must be an empty list")
        for field in ("computed_style_findings", "svg_findings", "canvas_gradient_calls"):
            values = viewport.get(field)
            if not isinstance(values, list) or values:
                errors.append(f"Live {name} {field} must be an empty list")
        for uri in viewport.get("data_uris", []) if isinstance(viewport.get("data_uris"), list) else []:
            if not isinstance(uri, dict) or uri.get("decode_error") or uri.get("truncated") is True or uri.get("scan_findings"):
                errors.append(f"Live {name} data URI was undecodable, truncated, or prohibited")
        viewport_claims = viewport.get("claim_candidates")
        if not isinstance(viewport_claims, list):
            errors.append(f"Live {name} claim_candidates must be a list")
        else:
            for claim in viewport_claims:
                if isinstance(claim, dict):
                    all_live_claims.add(
                        (str(claim.get("selector", "")).strip(), normalized(claim.get("text")))
                    )

        resources = viewport.get("first_party_resources")
        if not isinstance(resources, list) or not resources:
            errors.append(f"Live {name} audit must hash at least one loaded first-party resource")
        else:
            for resource in resources:
                if not isinstance(resource, dict):
                    errors.append(f"Live {name} first-party resource record is invalid")
                    continue
                if resource.get("first_party") is not True:
                    errors.append(f"Live {name} first-party resource classification is invalid")
                status = resource.get("status")
                if isinstance(status, bool) or not isinstance(status, int) or not 200 <= status < 400:
                    errors.append(f"Live {name} first-party resource returned an invalid status: {resource.get('url')}")
                elif 300 <= status < 400 and (
                    resource.get("redirect") is not True
                    or not isinstance(resource.get("redirect_location"), str)
                    or not resource.get("redirect_location")
                    or resource.get("byte_length") != 0
                ):
                    errors.append(f"Live {name} first-party redirect evidence is incomplete: {resource.get('url')}")
                if resource.get("body_error"):
                    errors.append(f"Live {name} first-party resource body could not be inspected: {resource.get('url')}")
                if not isinstance(resource.get("resource_type"), str) or not resource.get("resource_type"):
                    errors.append(f"Live {name} first-party resource type is missing: {resource.get('url')}")
                payload = decode_resource_body(
                    resource,
                    f"Live {name} first-party resource {resource.get('url')}",
                    errors,
                )
                sniffed_type = sniff_image_type(payload)
                if resource.get("sniffed_type", "") != sniffed_type:
                    errors.append(f"Live {name} first-party resource magic-byte type is inconsistent")
                if payload is not None:
                    scan_forbidden_content(
                        payload.decode("utf-8", errors="replace"),
                        f"loaded first-party resource {resource.get('url')}",
                        errors,
                    )
                if resource.get("body_truncated") is True:
                    errors.append(f"Live {name} first-party resource body cannot be truncated")
                if resource.get("scan_findings"):
                    errors.append(f"Live {name} loaded resource contains a prohibited visual pattern")
                if not re.fullmatch(r"[0-9a-f]{64}", str(resource.get("sha256", ""))):
                    errors.append(f"Live {name} loaded resource is missing a sha256")
                for uri in resource.get("data_uris", []) if isinstance(resource.get("data_uris"), list) else []:
                    if not isinstance(uri, dict) or uri.get("decode_error") or uri.get("truncated") is True or uri.get("scan_findings"):
                        errors.append(f"Live {name} loaded resource contains unsafe data URI evidence")
        external_resources = viewport.get("external_resources")
        if not isinstance(external_resources, list):
            errors.append(f"Live {name} external_resources must be a list")
        else:
            for resource in external_resources:
                if not isinstance(resource, dict):
                    errors.append(f"Live {name} external resource record is invalid")
                    continue
                if resource.get("first_party") is not False:
                    errors.append(f"Live {name} external resource classification is invalid")
                status = resource.get("status")
                if isinstance(status, bool) or not isinstance(status, int) or not 200 <= status < 400:
                    errors.append(f"Live {name} external resource returned an invalid status: {resource.get('url')}")
                elif 300 <= status < 400 and (
                    resource.get("redirect") is not True
                    or not isinstance(resource.get("redirect_location"), str)
                    or not resource.get("redirect_location")
                    or resource.get("byte_length") != 0
                ):
                    errors.append(f"Live {name} external redirect evidence is incomplete: {resource.get('url')}")
                if resource.get("body_error"):
                    errors.append(f"Live {name} external resource body could not be inspected: {resource.get('url')}")
                if not isinstance(resource.get("resource_type"), str) or not resource.get("resource_type"):
                    errors.append(f"Live {name} external resource type is missing: {resource.get('url')}")
                payload = decode_resource_body(
                    resource,
                    f"Live {name} external resource {resource.get('url')}",
                    errors,
                )
                sniffed_type = sniff_image_type(payload)
                if resource.get("sniffed_type", "") != sniffed_type:
                    errors.append(f"Live {name} external resource magic-byte type is inconsistent")
                if payload is not None:
                    scan_forbidden_content(
                        payload.decode("utf-8", errors="replace"),
                        f"loaded external resource {resource.get('url')}",
                        errors,
                    )
                content_type = str(resource.get("content_type", "")).casefold()
                resource_url = str(resource.get("url", ""))
                raster_types = {
                    "image/png", "image/jpeg", "image/gif", "image/webp", "image/avif", "image/bmp"
                }
                declared_raster = bool(
                    re.match(r"^image/(?:png|jpe?g|gif|webp|avif|bmp)", content_type)
                    or re.search(r"\.(?:png|jpe?g|gif|webp|avif|bmp)(?:[?#]|$)", resource_url, re.I)
                )
                uninspectable_visual = resource.get("resource_type") == "image" and not sniffed_type
                if declared_raster or sniffed_type in raster_types or uninspectable_visual:
                    errors.append(
                        f"Live {name} uses an externally mutable raster resource; localize and review it: {resource.get('url')}"
                    )
                if resource.get("body_truncated") is True:
                    errors.append(f"Live {name} external resource body cannot be truncated")
                if resource.get("scan_findings"):
                    errors.append(f"Live {name} external resource contains a prohibited visual pattern")
                if not re.fullmatch(r"[0-9a-f]{64}", str(resource.get("sha256", ""))):
                    errors.append(f"Live {name} external resource is missing a sha256")
                for uri in resource.get("data_uris", []) if isinstance(resource.get("data_uris"), list) else []:
                    if not isinstance(uri, dict) or uri.get("decode_error") or uri.get("truncated") is True or uri.get("scan_findings"):
                        errors.append(f"Live {name} external resource contains unsafe data URI evidence")

        signals = viewport.get("domain_signals")
        signal_identities: list[str] = []
        if (
            not isinstance(signals, list)
            or len(signals) != len(report_signal_selectors)
            or {item.get("selector") for item in signals if isinstance(item, dict)} != set(report_signal_selectors)
        ):
            errors.append(f"Live {name} domain signal inventory does not match the report")
        else:
            report_lookup = {
                item["selector"]: item
                for item in get_path(data, "product_specificity.domain_signals", [])
                if isinstance(item, dict) and isinstance(item.get("selector"), str)
            }
            for signal in signals:
                matches = signal.get("matches")
                if signal.get("count") != 1 or not isinstance(matches, list) or len(matches) != 1 or matches[0].get("visible") is not True:
                    errors.append(f"Live {name} domain selector must resolve to exactly one visible element: {signal.get('selector')}")
                    continue
                identity = matches[0].get("element_identity")
                if not isinstance(identity, str) or not identity:
                    errors.append(f"Live {name} domain selector lacks a stable element identity: {signal.get('selector')}")
                elif selector_is_overbroad(identity) or identity.casefold().endswith(" > main"):
                    errors.append(f"Live {name} domain selector resolves to an overbroad application container")
                else:
                    signal_identities.append(identity)
                if not live_signal_is_substantive(matches[0]):
                    errors.append(f"Live {name} domain selector is visually concealed or trivial: {signal.get('selector')}")
                visible_tokens = meaningful_tokens(matches[0].get("text"))
                detail_tokens = meaningful_tokens(report_lookup[signal["selector"]].get("domain_detail"))
                if not visible_tokens & detail_tokens:
                    errors.append(f"Live {name} domain selector text does not substantiate its report detail: {signal.get('selector')}")

        decisions = viewport.get("decision_signals")
        decision_identities: list[str] = []
        if (
            not isinstance(decisions, list)
            or len(decisions) != len(report_decision_selectors)
            or {item.get("selector") for item in decisions if isinstance(item, dict)} != set(report_decision_selectors)
        ):
            errors.append(f"Live {name} decision signal inventory does not match the report")
        else:
            report_lookup = {
                item["selector"]: item
                for item in get_path(data, "product_specificity.decision_points", [])
                if isinstance(item, dict) and isinstance(item.get("selector"), str)
            }
            for signal in decisions:
                matches = signal.get("matches")
                if signal.get("count") != 1 or not isinstance(matches, list) or len(matches) != 1 or matches[0].get("visible") is not True:
                    errors.append(f"Live {name} decision selector must resolve to exactly one visible element: {signal.get('selector')}")
                    continue
                identity = matches[0].get("element_identity")
                if not isinstance(identity, str) or not identity:
                    errors.append(f"Live {name} decision selector lacks a stable element identity: {signal.get('selector')}")
                elif selector_is_overbroad(identity) or identity.casefold().endswith(" > main"):
                    errors.append(f"Live {name} decision selector resolves to an overbroad application container")
                else:
                    decision_identities.append(identity)
                if not live_signal_is_substantive(matches[0]):
                    errors.append(f"Live {name} decision selector is visually concealed or trivial: {signal.get('selector')}")
                report_item = report_lookup[signal["selector"]]
                expected_tokens = meaningful_tokens(report_item.get("inputs")) | meaningful_tokens(report_item.get("consequence"))
                if len(meaningful_tokens(matches[0].get("text")) & expected_tokens) < 2:
                    errors.append(f"Live {name} decision selector text does not substantiate its inputs and consequence")
        combined_signal_identities = signal_identities + decision_identities
        if len(combined_signal_identities) != len(set(combined_signal_identities)):
            errors.append(f"Live {name} product and decision selectors collapse onto the same DOM element")

        flow = viewport.get("primary_flow")
        if not isinstance(flow, dict):
            errors.append(f"Live {name} primary_flow is missing")
            continue
        if flow.get("selector") != primary_selector or flow.get("recovery_selector") != recovery_selector:
            errors.append(f"Live {name} primary flow selectors differ from the executed config")
        if flow.get("ordered_stages") != ["start", "feedback", "terminal", "recovery"]:
            errors.append(f"Live {name} primary flow must preserve start→feedback→terminal→recovery")
        states = flow.get("states")
        if not isinstance(states, list) or len(states) != 4:
            errors.append(f"Live {name} primary flow must contain four captured states")
            continue
        if expected_file_entry is not None:
            start_path = file_url_path(states[0].get("url"), config_path.parent)
            if start_path != expected_file_entry:
                errors.append(
                    f"Live {name} start state redirected away from the canonical project index"
                )
            start_frames = states[0].get("frames") if isinstance(states[0], dict) else None
            if (
                not isinstance(start_frames, list)
                or not start_frames
                or file_url_path(start_frames[0].get("frame_url"), config_path.parent) != expected_file_entry
            ):
                errors.append(f"Live {name} top frame is not the canonical project index")
        screenshot_hashes: list[str] = []
        dom_hashes: list[str] = []
        text_hashes: list[str] = []
        for state in states:
            if not isinstance(state, dict):
                errors.append(f"Live {name} primary state is invalid")
                continue
            stage = state.get("stage")
            screenshot_hash = state.get("screenshot_sha256")
            screenshot_hashes.append(str(screenshot_hash))
            dom_hashes.append(str(state.get("dom_sha256")))
            text_hashes.append(str(state.get("visible_text_sha256")))
            live_path = resolve_path(
                state.get("screenshot_path"),
                config_path.parent,
                f"live_audit.{name}.{stage}.screenshot_path",
                errors,
            )
            record = captures_by_checkpoint.get((str(name), f"primary-{stage}"))
            if record is None:
                errors.append(f"Capture manifest is missing live {name} primary-{stage}")
            elif live_path != record.get("_artifact") or screenshot_hash != record.get("sha256"):
                errors.append(f"Live {name} primary-{stage} screenshot does not match the capture manifest")
            visible_text = state.get("visible_text")
            if not isinstance(visible_text, str) or len(visible_text.strip()) < 120:
                errors.append(f"Live {name} {stage} visible text is too thin for product validation")
        if len(set(screenshot_hashes)) != 4 or len(set(dom_hashes)) != 4 or len(set(text_hashes)) != 4:
            errors.append(f"Live {name} primary flow states must have distinct screenshot, DOM, and visible-text hashes")
        start_text = states[0].get("visible_text", "") if isinstance(states[0], dict) else ""
        visible_tokens = meaningful_tokens(start_text)
        contract_tokens = meaningful_tokens(get_path(data, "context.product_type")) | meaningful_tokens(get_path(data, "context.primary_task"))
        for domain_object in get_path(data, "context.domain_objects", []) or []:
            object_tokens = meaningful_tokens(domain_object)
            contract_tokens.update(object_tokens)
            if object_tokens and not object_tokens & visible_tokens:
                errors.append(f"Live {name} default route omits domain object: {domain_object}")
        if len(visible_tokens & contract_tokens) < min(6, len(contract_tokens)):
            errors.append(f"Live {name} default route does not expose enough product-contract vocabulary")

        actual_controls = viewport.get("controls")
        actual_keys: set[tuple[str, str]] = set()
        if not isinstance(actual_controls, list):
            errors.append(f"Live {name} controls must be a list")
        else:
            for control in actual_controls:
                key = live_control_key(control)
                if key is None:
                    errors.append(f"Live {name} control lacks a stable selector or accessible name")
                    continue
                if key in actual_keys:
                    errors.append(f"Live {name} control identity is duplicated: {key[0]}")
                actual_keys.add(key)
                if not isinstance(control.get("disabled"), bool):
                    errors.append(f"Live {name} control disabled state is missing: {key[0]}")
                reported_behavior = report_by_selector.get(key[0], {}).get("behavior")
                if control.get("disabled") is True and reported_behavior != "disabled":
                    errors.append(f"Live {name} control is unexpectedly disabled: {key[0]}")
                if reported_behavior == "disabled" and control.get("disabled") is not True:
                    errors.append(f"Live {name} control is declared disabled but remains actionable: {key[0]}")
                href = str(control.get("href", "")).strip().casefold()
                if href == "#" or href.startswith("javascript:"):
                    errors.append(f"Live {name} control has a dead placeholder href: {key[0]}")
        if actual_keys != report_control_keys:
            missing = sorted(report_control_keys - actual_keys)
            unreported = sorted(actual_keys - report_control_keys)
            errors.append(f"Live {name} control inventory differs from report; missing={missing}, unreported={unreported}")

        scenario_selectors = set(config_scenarios)
        extra_selectors = (
            {key[0] for key in actual_keys}
            - {str(primary_selector), str(recovery_selector)}
            - disabled_selectors
        )
        if scenario_selectors != extra_selectors:
            errors.append(
                f"Live {name} actionable non-primary controls need exact fresh-context scenarios; "
                f"expected={sorted(extra_selectors)}, configured={sorted(scenario_selectors)}"
            )
        scenarios = viewport.get("control_scenarios")
        result_selectors = {
            item.get("selector") for item in scenarios if isinstance(item, dict)
        } if isinstance(scenarios, list) else set()
        if not isinstance(scenarios, list) or result_selectors != extra_selectors or len(scenarios) != len(extra_selectors):
            errors.append(f"Live {name} control scenario results are incomplete or duplicated")
        else:
            for scenario in scenarios:
                selector = scenario.get("selector")
                spec = config_scenarios.get(selector, {})
                expected_public = {
                    "action": spec.get("action", "click"),
                    "setup": spec.get("setup", "default"),
                    "value": spec.get("value"),
                    "key": spec.get("key"),
                    "expected_selector": spec.get("expected_selector", ""),
                    "expected_url_pattern": spec.get("expected_url_pattern", ""),
                    "expected_value": spec.get("expected_value"),
                    "expected_checked": spec.get("expected_checked"),
                }
                for field, expected in expected_public.items():
                    if scenario.get(field) != expected:
                        errors.append(
                            f"Live {name} control scenario {selector} does not match config field {field}"
                        )
                if scenario.get("matched_count") != 1:
                    errors.append(f"Live {name} control scenario must target exactly one element: {selector}")
                if scenario.get("disabled") is not False:
                    errors.append(f"Live {name} control scenario target is disabled or unverified: {selector}")
                if (
                    isinstance(scenario.get("async_activity_marker"), bool)
                    or not isinstance(scenario.get("async_activity_marker"), int)
                ):
                    errors.append(f"Live {name} control scenario lacks an async activity marker: {selector}")
                if not isinstance(scenario.get("pending_action_async"), list) or scenario.get("pending_action_async"):
                    errors.append(f"Live {name} control scenario left unsettled async work: {selector}")
                if scenario.get("passed") is not True or scenario.get("error"):
                    errors.append(f"Live {name} control scenario failed: {selector}")
                before = scenario.get("before") if isinstance(scenario.get("before"), dict) else {}
                after = scenario.get("after") if isinstance(scenario.get("after"), dict) else {}
                target_before = (
                    scenario.get("target_state_before")
                    if isinstance(scenario.get("target_state_before"), dict)
                    else {}
                )
                target_after = (
                    scenario.get("target_state_after")
                    if isinstance(scenario.get("target_state_after"), dict)
                    else {}
                )
                document_changed = (
                    before.get("dom_sha256") != after.get("dom_sha256")
                    or before.get("url") != after.get("url")
                    or before.get("visible_text_sha256") != after.get("visible_text_sha256")
                )
                target_changed = (
                    target_before.get("value") != target_after.get("value")
                    or target_before.get("checked") != target_after.get("checked")
                )
                if scenario.get("meaningful_change") is not True or not (document_changed or target_changed):
                    errors.append(f"Live {name} control scenario produced no observable state change: {selector}")
                if spec.get("expected_selector") and (
                    scenario.get("expected_selector_visible_before") is not False
                    or scenario.get("expected_selector_visible_after") is not True
                ):
                    errors.append(f"Live {name} expected selector did not transition for: {selector}")
                if spec.get("expected_url_pattern") and (
                    scenario.get("expected_url_matched_before") is not False
                    or scenario.get("expected_url_matched_after") is not True
                ):
                    errors.append(f"Live {name} expected URL did not transition for: {selector}")
                if "expected_value" in spec and (
                    target_before.get("value") == spec.get("expected_value")
                    or target_after.get("value") != spec.get("expected_value")
                ):
                    errors.append(f"Live {name} expected value was not caused by the action: {selector}")
                if "expected_checked" in spec and (
                    target_before.get("checked") == spec.get("expected_checked")
                    or target_after.get("checked") != spec.get("expected_checked")
                ):
                    errors.append(f"Live {name} expected checked state was not caused by the action: {selector}")

    if all_live_claims != manifest_claims:
        missing = sorted(all_live_claims - manifest_claims)
        stale = sorted(manifest_claims - all_live_claims)
        errors.append(f"Live visible claim inventory differs from content_manifest; missing={missing}, stale={stale}")

    output_dir = resolve_path(config.get("output_dir"), config_path.parent, "live_audit_config.output_dir", errors)
    if output_dir is not None:
        saved_bundle = output_dir / "live-audit-bundle.json"
        if not saved_bundle.is_file():
            errors.append("Gate-owned live audit did not persist live-audit-bundle.json")


def paeth(left: int, above: int, upper_left: int) -> int:
    estimate = left + above - upper_left
    left_distance = abs(estimate - left)
    above_distance = abs(estimate - above)
    upper_left_distance = abs(estimate - upper_left)
    if left_distance <= above_distance and left_distance <= upper_left_distance:
        return left
    if above_distance <= upper_left_distance:
        return above
    return upper_left


def decode_png(path: Path, label: str, errors: list[str]) -> dict[str, Any] | None:
    try:
        content = path.read_bytes()
    except OSError as exc:
        errors.append(f"Unable to read PNG {label}: {exc}")
        return None
    if not content.startswith(b"\x89PNG\r\n\x1a\n"):
        errors.append(f"Browser evidence must be a PNG: {label}")
        return None
    content_digest = hashlib.sha256(content).hexdigest()
    cached = PNG_DECODE_CACHE.get(content_digest)
    if cached is not None:
        return cached

    offset = 8
    header: tuple[int, int, int, int, int, int, int] | None = None
    idat = bytearray()
    saw_iend = False
    while offset + 12 <= len(content):
        length = struct.unpack(">I", content[offset : offset + 4])[0]
        kind = content[offset + 4 : offset + 8]
        data_start = offset + 8
        data_end = data_start + length
        crc_end = data_end + 4
        if crc_end > len(content):
            errors.append(f"Truncated PNG chunk in {label}")
            return None
        payload = content[data_start:data_end]
        stored_crc = struct.unpack(">I", content[data_end:crc_end])[0]
        actual_crc = zlib.crc32(kind + payload) & 0xFFFFFFFF
        if stored_crc != actual_crc:
            errors.append(f"PNG CRC mismatch in {label}")
            return None
        if kind == b"IHDR":
            if header is not None or length != 13:
                errors.append(f"Invalid PNG IHDR in {label}")
                return None
            header = struct.unpack(">IIBBBBB", payload)
        elif kind == b"IDAT":
            idat.extend(payload)
        elif kind == b"IEND":
            saw_iend = True
            offset = crc_end
            break
        offset = crc_end

    if header is None or not idat or not saw_iend or offset != len(content):
        errors.append(f"PNG is incomplete or has trailing bytes: {label}")
        return None
    width, height, bit_depth, color_type, compression, filter_method, interlace = header
    if width < 1 or height < 1 or width * height > MAX_IMAGE_PIXELS:
        errors.append(f"PNG dimensions are invalid or excessive in {label}: {width}x{height}")
        return None
    channels = {0: 1, 2: 3, 4: 2, 6: 4}.get(color_type)
    if (
        bit_depth != 8
        or channels is None
        or compression != 0
        or filter_method != 0
        or interlace != 0
    ):
        errors.append(
            f"PNG must be non-interlaced 8-bit gray/RGB/RGBA browser evidence: {label}"
        )
        return None
    row_bytes = width * channels
    expected = (row_bytes + 1) * height
    try:
        inflated = zlib.decompress(bytes(idat))
    except zlib.error as exc:
        errors.append(f"PNG IDAT cannot be decoded in {label}: {exc}")
        return None
    if len(inflated) != expected:
        errors.append(
            f"PNG decoded length mismatch in {label}: expected {expected}, got {len(inflated)}"
        )
        return None

    rows: list[bytearray] = []
    cursor = 0
    previous = bytearray(row_bytes)
    for _ in range(height):
        filter_type = inflated[cursor]
        cursor += 1
        encoded = inflated[cursor : cursor + row_bytes]
        cursor += row_bytes
        if filter_type > 4:
            errors.append(f"Unsupported PNG row filter in {label}")
            return None
        decoded = bytearray(row_bytes)
        for index, value in enumerate(encoded):
            left = decoded[index - channels] if index >= channels else 0
            above = previous[index]
            upper_left = previous[index - channels] if index >= channels else 0
            if filter_type == 0:
                predictor = 0
            elif filter_type == 1:
                predictor = left
            elif filter_type == 2:
                predictor = above
            elif filter_type == 3:
                predictor = (left + above) // 2
            else:
                predictor = paeth(left, above, upper_left)
            decoded[index] = (value + predictor) & 0xFF
        rows.append(decoded)
        previous = decoded

    rgb = bytearray(width * height * 3)
    target = 0
    for row in rows:
        for offset in range(0, len(row), channels):
            if color_type in {0, 4}:
                red = green = blue = row[offset]
            else:
                red, green, blue = row[offset : offset + 3]
            rgb[target : target + 3] = bytes((red, green, blue))
            target += 3
    decoded_result = {
        "width": width,
        "height": height,
        "rgb": bytes(rgb),
        "pixel_digest": hashlib.sha256(bytes(rgb)).hexdigest(),
        "file_digest": content_digest,
    }
    if len(PNG_DECODE_CACHE) >= 96:
        PNG_DECODE_CACHE.pop(next(iter(PNG_DECODE_CACHE)))
    PNG_DECODE_CACHE[content_digest] = decoded_result
    return decoded_result


def pixel_change_ratio(first: dict[str, Any], second: dict[str, Any]) -> float:
    if first["width"] != second["width"] or first["height"] != second["height"]:
        return 1.0
    first_rgb: bytes = first["rgb"]
    second_rgb: bytes = second["rgb"]
    pixels = len(first_rgb) // 3
    if not pixels:
        return 0.0
    changed = 0
    step = max(1, pixels // 300_000)
    sampled = 0
    for pixel in range(0, pixels, step):
        start = pixel * 3
        distance = sum(abs(first_rgb[start + channel] - second_rgb[start + channel]) for channel in range(3))
        sampled += 1
        if distance >= 24:
            changed += 1
    return changed / sampled if sampled else 0.0


def image_structure_metrics(decoded: dict[str, Any]) -> tuple[float, int]:
    """Return mean adjacent-channel delta and sampled color diversity."""
    cached = decoded.get("_structure_metrics")
    if isinstance(cached, tuple) and len(cached) == 2:
        return cached
    rgb: bytes = decoded["rgb"]
    width = decoded["width"]
    height = decoded["height"]
    pixels = width * height
    step = max(1, pixels // 200_000)
    total_delta = 0
    comparisons = 0
    colors: set[bytes] = set()
    for pixel in range(0, pixels, step):
        start = pixel * 3
        colors.add(rgb[start : start + 3])
        if pixel % width != width - 1:
            next_start = start + 3
            total_delta += sum(
                abs(rgb[start + channel] - rgb[next_start + channel]) for channel in range(3)
            )
            comparisons += 3
    mean_delta = total_delta / comparisons if comparisons else 0.0
    result = (mean_delta, len(colors))
    decoded["_structure_metrics"] = result
    return result


def collect_report_images(value: Any, base_dir: Path, found: set[Path]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"artifact", "screenshot", "desktop", "mobile"} and isinstance(child, str):
                candidate = Path(child).expanduser()
                if candidate.suffix.casefold() in BROWSER_IMAGE_SUFFIXES:
                    if not candidate.is_absolute():
                        candidate = base_dir / candidate
                    try:
                        found.add(candidate.resolve())
                    except OSError:
                        pass
            collect_report_images(child, base_dir, found)
    elif isinstance(value, list):
        for child in value:
            collect_report_images(child, base_dir, found)


def validate_capture_manifest(
    data: dict[str, Any],
    base_dir: Path,
    source_fingerprint: str | None,
    errors: list[str],
) -> tuple[dict[Path, dict[str, Any]], Path | None]:
    manifest, manifest_path = load_json_file(
        get_path(data, "implementation_audit.capture_manifest"),
        base_dir,
        "implementation_audit.capture_manifest",
        errors,
    )
    if manifest is None or manifest_path is None:
        return {}, manifest_path
    require_manifest_header(manifest, CAPTURE_GENERATOR, "capture_manifest", errors)
    if source_fingerprint and manifest.get("source_fingerprint") != source_fingerprint:
        errors.append("capture_manifest.source_fingerprint does not match the scanned source tree")
    captures = manifest.get("captures")
    if not isinstance(captures, list) or len(captures) < 8:
        errors.append("capture_manifest.captures must contain at least eight browser checkpoints")
        return {}, manifest_path

    records: dict[Path, dict[str, Any]] = {}
    pixel_digests: set[str] = set()
    timestamps: list[float] = []
    for index, record in enumerate(captures):
        path = f"capture_manifest.captures[{index}]"
        if not isinstance(record, dict):
            errors.append(f"Capture must be an object: {path}")
            continue
        artifact = resolve_path(record.get("artifact"), manifest_path.parent, f"{path}.artifact", errors)
        if artifact is None or not artifact.is_file():
            errors.append(f"Capture artifact does not exist: {path}")
            continue
        if artifact.suffix.casefold() != ".png":
            errors.append(f"Capture artifact must be PNG: {path}")
            continue
        decoded = decode_png(artifact, path, errors)
        if decoded is None:
            continue
        mean_delta, color_count = image_structure_metrics(decoded)
        if mean_delta > 70:
            errors.append(
                f"Capture resembles high-frequency noise rather than a browser surface: {path} "
                f"(adjacent delta {mean_delta:.2f})"
            )
        if color_count < 4:
            errors.append(f"Capture is visually trivial or blank: {path} ({color_count} sampled colors)")
        if record.get("sha256") != decoded["file_digest"]:
            errors.append(f"Capture sha256 mismatch: {path}")
        if record.get("width") != decoded["width"] or record.get("height") != decoded["height"]:
            errors.append(f"Capture dimensions do not match PNG: {path}")
        viewport = record.get("viewport")
        if viewport not in {"desktop", "mobile"}:
            errors.append(f"{path}.viewport must be desktop or mobile")
        if viewport == "desktop" and decoded["width"] < 640:
            errors.append(f"Desktop capture is too narrow: {path}")
        if viewport == "mobile" and decoded["width"] > 600:
            errors.append(f"Mobile capture is too wide: {path}")
        if not isinstance(record.get("route"), str) or len(record["route"].strip()) < 1:
            errors.append(f"{path}.route is required")
        if not isinstance(record.get("state"), str) or len(record["state"].strip()) < 3:
            errors.append(f"{path}.state is required")
        if not isinstance(record.get("checkpoint"), str) or len(record["checkpoint"].strip()) < 3:
            errors.append(f"{path}.checkpoint is required")
        captured_at = parse_timestamp(record.get("captured_at"), f"{path}.captured_at", errors)
        if captured_at is not None:
            timestamps.append(captured_at)
        if decoded["pixel_digest"] in pixel_digests:
            errors.append(f"Capture reuses identical decoded pixels under a different claim: {path}")
        pixel_digests.add(decoded["pixel_digest"])
        if artifact in records:
            errors.append(f"Capture artifact is listed more than once: {path}")
        record_copy = dict(record)
        record_copy["_artifact"] = artifact
        record_copy["_decoded"] = decoded
        record_copy["_captured_at"] = captured_at
        records[artifact] = record_copy

    if timestamps != sorted(timestamps) or len(timestamps) != len(set(timestamps)):
        errors.append("capture_manifest.captures must be listed in strict chronological order")

    report_images: set[Path] = set()
    collect_report_images(data, base_dir, report_images)
    for artifact in sorted(report_images, key=lambda item: str(item).casefold()):
        if artifact not in records:
            errors.append(f"Report image is missing from capture_manifest: {artifact}")
    return records, manifest_path


def validate_style_manifests(
    data: dict[str, Any], base_dir: Path, source_fingerprint: str | None, errors: list[str]
) -> None:
    values = get_path(data, "implementation_audit.runtime_style_manifests")
    if not isinstance(values, list) or len(values) < 2:
        errors.append("implementation_audit.runtime_style_manifests must contain desktop and mobile JSON")
        return
    viewports: set[str] = set()
    manifest_files: set[Path] = set()
    for index, value in enumerate(values):
        path = f"implementation_audit.runtime_style_manifests[{index}]"
        manifest, manifest_path = load_json_file(value, base_dir, path, errors)
        if manifest is None or manifest_path is None:
            continue
        if manifest_path in manifest_files:
            errors.append(f"Runtime style manifests must be distinct files: {path}")
        manifest_files.add(manifest_path)
        require_manifest_header(manifest, STYLE_GENERATOR, path, errors)
        if source_fingerprint and manifest.get("source_fingerprint") != source_fingerprint:
            errors.append(f"{path}.source_fingerprint does not match the scanned source tree")
        viewport = manifest.get("viewport")
        if viewport not in {"desktop", "mobile"}:
            errors.append(f"{path}.viewport must be desktop or mobile")
        else:
            viewports.add(viewport)
        parse_timestamp(manifest.get("captured_at"), f"{path}.captured_at", errors)
        if not isinstance(manifest.get("url"), str) or len(manifest["url"].strip()) < 4:
            errors.append(f"{path}.url is required")
        scanned = manifest.get("scanned_elements")
        if isinstance(scanned, bool) or not isinstance(scanned, int) or scanned < 1:
            errors.append(f"{path}.scanned_elements must be a positive integer")
        if manifest.get("pseudo_elements_checked") is not True:
            errors.append(f"{path}.pseudo_elements_checked must be true")
        if manifest.get("canvas_and_svg_checked") is not True:
            errors.append(f"{path}.canvas_and_svg_checked must be true")
        if manifest.get("canvas_elements_reviewed") is not True:
            errors.append(f"{path}.canvas_elements_reviewed must be true")
        for field in STYLE_EMPTY_FIELDS:
            findings = manifest.get(field)
            if not isinstance(findings, list) or findings:
                errors.append(f"{path}.{field} must be an empty list")
    if viewports != {"desktop", "mobile"}:
        errors.append("Runtime style audit must cover both desktop and mobile")


def validate_control_manifests(
    data: dict[str, Any], base_dir: Path, source_fingerprint: str | None, errors: list[str]
) -> None:
    values = get_path(data, "implementation_audit.control_manifests")
    if not isinstance(values, list) or len(values) < 2:
        errors.append("implementation_audit.control_manifests must contain desktop and mobile JSON")
        return
    context_cta = normalized(get_path(data, "context.primary_cta"))
    report_controls = get_path(data, "action_trace.control_inventory", [])
    report_keys = {
        (
            normalized(item.get("label")),
            normalized(item.get("accessible_name")),
            normalized(item.get("role")),
            str(item.get("selector", "")).strip(),
            item.get("behavior"),
        )
        for item in report_controls
        if isinstance(item, dict)
    }
    viewports: set[str] = set()
    for index, value in enumerate(values):
        path = f"implementation_audit.control_manifests[{index}]"
        manifest, _ = load_json_file(value, base_dir, path, errors)
        if manifest is None:
            continue
        require_manifest_header(manifest, CONTROL_GENERATOR, path, errors)
        if source_fingerprint and manifest.get("source_fingerprint") != source_fingerprint:
            errors.append(f"{path}.source_fingerprint does not match the scanned source tree")
        viewport = manifest.get("viewport")
        if viewport not in {"desktop", "mobile"}:
            errors.append(f"{path}.viewport must be desktop or mobile")
        else:
            viewports.add(viewport)
        parse_timestamp(manifest.get("captured_at"), f"{path}.captured_at", errors)
        if manifest.get("all_visible_controls_tested") is not True:
            errors.append(f"{path}.all_visible_controls_tested must be true")
        for field in ("dead_controls", "unreported_controls"):
            value_list = manifest.get(field)
            if not isinstance(value_list, list) or value_list:
                errors.append(f"{path}.{field} must be an empty list")
        controls = manifest.get("controls")
        if not isinstance(controls, list) or not controls:
            errors.append(f"{path}.controls must contain the rendered control inventory")
            continue
        manifest_keys: set[tuple[str, str, str, str, Any]] = set()
        primary_matches = 0
        for control_index, control in enumerate(controls):
            control_path = f"{path}.controls[{control_index}]"
            if not isinstance(control, dict):
                errors.append(f"Control must be an object: {control_path}")
                continue
            label = normalized(control.get("label"))
            accessible_name = normalized(control.get("accessible_name"))
            role = normalized(control.get("role"))
            selector = control.get("selector")
            behavior = control.get("behavior")
            manifest_keys.add(
                (
                    label,
                    accessible_name,
                    role,
                    selector.strip() if isinstance(selector, str) else "",
                    behavior,
                )
            )
            if len(label) < 2 or len(accessible_name) < 2:
                errors.append(f"{control_path} needs visible and accessible names")
            if not isinstance(selector, str) or len(selector.strip()) < 2:
                errors.append(f"{control_path}.selector is required")
            if behavior not in {"functional", "navigation", "disabled"}:
                errors.append(f"{control_path}.behavior is invalid")
            raw_href = (
                control.get("href", "").strip().casefold()
                if isinstance(control.get("href", ""), str)
                else ""
            )
            if raw_href == "#" or raw_href.startswith("javascript:"):
                errors.append(f"Dead or placeholder href found: {control_path}")
            if behavior == "navigation" and not raw_href:
                errors.append(f"Navigation control requires a real href: {control_path}")
            if behavior in {"functional", "navigation"}:
                if control.get("meaningful_change") is not True:
                    errors.append(f"{control_path}.meaningful_change must be true")
                before_hash = control.get("before_state_hash")
                after_hash = control.get("after_state_hash")
                before_url = control.get("before_url")
                after_url = control.get("after_url")
                if before_hash == after_hash and before_url == after_url:
                    errors.append(f"{control_path} has no observed URL or state change")
                for field in ("expected_result", "observed_result", "recovery"):
                    if not isinstance(control.get(field), str) or len(control[field].strip()) < 20:
                        errors.append(f"{control_path}.{field} must describe observed behavior")
            if label == context_cta:
                primary_matches += 1
                if role != "primary" or behavior != "functional":
                    errors.append(
                        f"{control_path} matching context.primary_cta must be primary and functional"
                    )
        if manifest_keys != report_keys:
            errors.append(f"{path}.controls must match action_trace.control_inventory exactly")
        if primary_matches != 1:
            errors.append(f"{path} must contain exactly one tested context.primary_cta")
    if viewports != {"desktop", "mobile"}:
        errors.append("Control audit must cover both desktop and mobile")


def validate_content_manifest(
    data: dict[str, Any],
    base_dir: Path,
    source_fingerprint: str | None,
    captures: dict[Path, dict[str, Any]],
    errors: list[str],
) -> None:
    manifest, _ = load_json_file(
        get_path(data, "implementation_audit.content_manifest"),
        base_dir,
        "implementation_audit.content_manifest",
        errors,
    )
    if manifest is None:
        return
    require_manifest_header(manifest, CONTENT_GENERATOR, "content_manifest", errors)
    if source_fingerprint and manifest.get("source_fingerprint") != source_fingerprint:
        errors.append("content_manifest.source_fingerprint does not match the scanned source tree")
    parse_timestamp(manifest.get("captured_at"), "content_manifest.captured_at", errors)
    if manifest.get("inventory_complete") is not True:
        errors.append("content_manifest.inventory_complete must be true")
    unverified = manifest.get("unverified_claims")
    if not isinstance(unverified, list) or unverified:
        errors.append("content_manifest.unverified_claims must be an empty list")
    claims = manifest.get("visible_claims")
    if not isinstance(claims, list):
        errors.append("content_manifest.visible_claims must be a list")
        return
    capture_hashes = {record["_decoded"]["file_digest"] for record in captures.values()}
    valid_claim_types = {
        "certification",
        "customer",
        "factual-data",
        "integration",
        "metric",
        "mock-data",
        "performance",
        "testimonial",
    }
    valid_source_types = {"external-research", "fixture", "repository", "user"}
    for index, claim in enumerate(claims):
        path = f"content_manifest.visible_claims[{index}]"
        if not isinstance(claim, dict):
            errors.append(f"Claim must be an object: {path}")
            continue
        for field, minimum in (("text", 5), ("selector", 2), ("source", 5)):
            if not isinstance(claim.get(field), str) or len(claim[field].strip()) < minimum:
                errors.append(f"{path}.{field} is required")
        if claim.get("claim_type") not in valid_claim_types:
            errors.append(f"{path}.claim_type is invalid")
        source_type = claim.get("source_type")
        if source_type not in valid_source_types:
            errors.append(f"{path}.source_type is invalid")
        source = claim.get("source")
        if source_type == "external-research" and (
            not isinstance(source, str) or not source.startswith(("http://", "https://"))
        ):
            errors.append(f"{path}.source must be an external URL")
        if source_type == "repository" and isinstance(source, str):
            source_path = resolve_path(source, base_dir, f"{path}.source", errors)
            if source_path is None or not source_path.is_file():
                errors.append(f"{path}.source repository artifact does not exist")
        if source_type == "fixture":
            disclosure = claim.get("disclosure")
            if not isinstance(disclosure, str) or len(disclosure.strip()) < 15:
                errors.append(f"{path}.disclosure must visibly identify fixture or demo data")
        if claim.get("evidence_capture_sha256") not in capture_hashes:
            errors.append(f"{path}.evidence_capture_sha256 is outside the capture manifest")


def evidence_artifact(value: Any, data: dict[str, Any], base_dir: Path) -> Path | None:
    if isinstance(value, str):
        catalog = data.get("evidence_catalog")
        if not isinstance(catalog, dict):
            return None
        value = catalog.get(value)
    if not isinstance(value, dict):
        return None
    artifact = value.get("artifact")
    if not isinstance(artifact, str):
        return None
    candidate = Path(artifact).expanduser()
    if not candidate.is_absolute():
        candidate = base_dir / candidate
    try:
        return candidate.resolve()
    except OSError:
        return None


def validate_checkpoint_sequence(
    checkpoints: Any,
    path: str,
    viewport: str,
    data: dict[str, Any],
    base_dir: Path,
    captures: dict[Path, dict[str, Any]],
    errors: list[str],
) -> None:
    if not isinstance(checkpoints, dict):
        errors.append(f"{path} must be an object with start, feedback, terminal, and recovery evidence")
        return
    ordered_records: list[dict[str, Any]] = []
    for name in ("start", "feedback", "terminal", "recovery"):
        artifact = evidence_artifact(checkpoints.get(name), data, base_dir)
        if artifact is None or artifact not in captures:
            errors.append(f"{path}.{name} must reference a capture-manifest screenshot")
            continue
        record = captures[artifact]
        if record.get("viewport") != viewport:
            errors.append(f"{path}.{name} must use a {viewport} capture")
        if normalized(record.get("checkpoint")) != normalized(f"primary-{name}"):
            errors.append(f"{path}.{name} capture checkpoint must be 'primary-{name}'")
        ordered_records.append(record)
    if len(ordered_records) != 4:
        return
    times = [record.get("_captured_at") for record in ordered_records]
    if any(value is None for value in times) or times != sorted(times) or len(set(times)) != 4:
        errors.append(f"{path} must be captured in strict start→feedback→terminal→recovery order")
    for first, second in zip(ordered_records, ordered_records[1:]):
        ratio = pixel_change_ratio(first["_decoded"], second["_decoded"])
        if ratio < 0.001:
            errors.append(
                f"{path} consecutive checkpoints are visually indistinguishable ({ratio:.4%} changed)"
            )


def validate_action_and_state_evidence(
    data: dict[str, Any],
    base_dir: Path,
    captures: dict[Path, dict[str, Any]],
    errors: list[str],
) -> None:
    label = normalized(get_path(data, "context.primary_cta"))
    if any(pattern.search(label) for pattern in GENERIC_CTA_PATTERNS):
        errors.append("context.primary_cta uses a generic prefix or suffix-resistant vague label")
    label_tokens = meaningful_tokens(get_path(data, "context.primary_cta"))
    contract_tokens = meaningful_tokens(get_path(data, "context.primary_task"))
    for domain_object in get_path(data, "context.domain_objects", []) or []:
        contract_tokens.update(meaningful_tokens(domain_object))
    if not label_tokens & contract_tokens:
        errors.append("context.primary_cta must name a product object or task outcome")

    inventory = get_path(data, "action_trace.control_inventory", [])
    matching = [item for item in inventory if isinstance(item, dict) and normalized(item.get("label")) == label]
    if len(matching) != 1:
        errors.append("action_trace.control_inventory must contain exactly one context.primary_cta")
    elif matching[0].get("role") != "primary" or matching[0].get("behavior") != "functional":
        errors.append("The context.primary_cta control must itself be primary and functional")

    validate_checkpoint_sequence(
        get_path(data, "action_trace.primary.checkpoints"),
        "action_trace.primary.checkpoints",
        "desktop",
        data,
        base_dir,
        captures,
        errors,
    )
    walkthroughs = get_path(data, "task_walkthroughs", [])
    if isinstance(walkthroughs, list):
        for index, walkthrough in enumerate(walkthroughs):
            if not isinstance(walkthrough, dict):
                continue
            viewport = walkthrough.get("viewport")
            if viewport in {"desktop", "mobile"}:
                validate_checkpoint_sequence(
                    walkthrough.get("checkpoints"),
                    f"task_walkthroughs[{index}].checkpoints",
                    viewport,
                    data,
                    base_dir,
                    captures,
                    errors,
                )

    state_artifacts: dict[str, Path] = {}
    states = get_path(data, "state_coverage", [])
    if isinstance(states, list):
        for item in states:
            if not isinstance(item, dict) or item.get("status") != "implemented":
                continue
            evidence = item.get("evidence")
            if isinstance(evidence, list) and evidence:
                artifact = evidence_artifact(evidence[0], data, base_dir)
                if artifact is not None:
                    state_artifacts[str(item.get("state"))] = artifact
    success = state_artifacts.get("success")
    long_content = state_artifacts.get("long-content")
    if success and long_content and success in captures and long_content in captures:
        if captures[success]["_decoded"]["pixel_digest"] == captures[long_content]["_decoded"]["pixel_digest"]:
            errors.append("success and long-content states must use state-specific decoded pixels")

    trait_requirements = {
        "async": {"loading", "error"},
        "form": {"disabled", "error"},
        "collection": {"empty", "long-content"},
        "generation": {"loading", "error", "success"},
        "transaction": {"disabled", "error", "success"},
    }
    traits = get_path(data, "context.task_traits", [])
    required: set[str] = set()
    if isinstance(traits, list):
        for trait in traits:
            required.update(trait_requirements.get(normalized(trait), set()))
    implemented = {
        str(item.get("state"))
        for item in states
        if isinstance(item, dict) and item.get("status") == "implemented"
    }
    for state in sorted(required - implemented):
        errors.append(f"context.task_traits require state_coverage.{state} to be implemented")

    loading = get_path(data, "loading_experience")
    loading_required = bool({normalized(trait) for trait in traits or []} & {"async", "generation"})
    if not isinstance(loading, dict):
        if loading_required:
            errors.append("async and generation traits require loading_experience")
        return
    applicable = loading.get("applicable")
    boundaries = loading.get("boundaries")
    if not isinstance(applicable, bool):
        errors.append("loading_experience.applicable must be a boolean")
    if not isinstance(boundaries, list):
        errors.append("loading_experience.boundaries must be a list")
        return
    if loading_required and applicable is not True:
        errors.append("async and generation traits require loading_experience.applicable=true")
    if loading_required and not boundaries:
        errors.append("async and generation traits require at least one loading boundary")
    if applicable is False and boundaries:
        errors.append("loading_experience.boundaries must be empty when loading is not applicable")
    for index, boundary in enumerate(boundaries):
        path = f"loading_experience.boundaries[{index}]"
        if not isinstance(boundary, dict):
            errors.append(f"{path} must be an object")
            continue
        for key in (
            "trigger",
            "affected_surface",
            "wait_avoidance",
            "stale_data_policy",
            "failure_recovery",
            "user_control",
            "evidence",
        ):
            if not isinstance(boundary.get(key), str) or not boundary.get(key, "").strip():
                errors.append(f"{path}.{key} must be non-empty")


def validate_substitution(data: dict[str, Any], errors: list[str]) -> None:
    comparisons = get_path(data, "product_specificity.substitution_test.comparisons", [])
    if not isinstance(comparisons, list):
        return
    target_tokens = meaningful_tokens(get_path(data, "context.product_type"))
    for item in get_path(data, "context.domain_objects", []) or []:
        target_tokens.update(meaningful_tokens(item))
    alternates: list[set[str]] = []
    for index, comparison in enumerate(comparisons):
        path = f"product_specificity.substitution_test.comparisons[{index}]"
        if not isinstance(comparison, dict):
            continue
        alternate_tokens = meaningful_tokens(comparison.get("alternate_product"))
        alternates.append(alternate_tokens)
        overlap = target_tokens & alternate_tokens
        if overlap:
            errors.append(f"{path}.alternate_product is not semantically distant; shared tokens: {sorted(overlap)}")
        if comparison.get("far_from_target") is not True:
            errors.append(f"{path}.far_from_target must be true")
        rationale = comparison.get("distance_rationale")
        if not isinstance(rationale, str) or len(rationale.strip()) < 50:
            errors.append(f"{path}.distance_rationale must justify a distant domain")
        axes = comparison.get("axes")
        if not isinstance(axes, dict) or set(axes) != set(SUBSTITUTION_AXES):
            errors.append(f"{path}.axes must contain exactly {list(SUBSTITUTION_AXES)}")
        else:
            broken = 0
            for axis in SUBSTITUTION_AXES:
                record = axes.get(axis)
                axis_path = f"{path}.axes.{axis}"
                if not isinstance(record, dict):
                    errors.append(f"{axis_path} must be an object")
                    continue
                if record.get("breaks") is True:
                    broken += 1
                reason = record.get("reason")
                if not isinstance(reason, str) or len(reason.strip()) < 25:
                    errors.append(f"{axis_path}.reason must be concrete")
            if broken < 4:
                errors.append(f"{path} must structurally break on at least four of five axes")
        for signal_index, signal in enumerate(comparison.get("breaking_signals") or []):
            signal_tokens = meaningful_tokens(signal)
            if signal_tokens & COSMETIC_TERMS and not signal_tokens & target_tokens:
                errors.append(
                    f"{path}.breaking_signals[{signal_index}] relies on cosmetic identity"
                )
    if len(alternates) >= 2 and alternates[0] & alternates[1]:
        errors.append("Substitution alternate products must be mutually distant, not adjacent categories")


def validate_iteration_evidence(
    data: dict[str, Any], base_dir: Path, captures: dict[Path, dict[str, Any]], errors: list[str]
) -> None:
    iterations = get_path(data, "visual_review.iteration_log", [])
    if not isinstance(iterations, list):
        return
    records: list[dict[str, Any]] = []
    findings: set[str] = set()
    resolved: set[str] = set()
    for index, iteration in enumerate(iterations):
        if not isinstance(iteration, dict):
            continue
        screenshot = resolve_path(
            iteration.get("screenshot"), base_dir, f"visual_review.iteration_log[{index}].screenshot", errors
        )
        if screenshot in captures:
            records.append(captures[screenshot])
        for finding_index, finding in enumerate(iteration.get("findings") or []):
            if not isinstance(finding, dict):
                continue
            finding_id = normalized(finding.get("id"))
            if len(finding_id) < 3:
                errors.append(
                    f"visual_review.iteration_log[{index}].findings[{finding_index}].id is required"
                )
            elif finding_id in findings:
                errors.append(f"Duplicate iteration finding id: {finding_id}")
            else:
                findings.add(finding_id)
        for change_index, change in enumerate(iteration.get("changes") or []):
            if not isinstance(change, dict):
                continue
            resolves = change.get("resolves")
            if not isinstance(resolves, list) or not resolves:
                errors.append(
                    f"visual_review.iteration_log[{index}].changes[{change_index}].resolves is required"
                )
                continue
            for finding_id in resolves:
                resolved.add(normalized(finding_id))
    if len(records) == len(iterations) and records:
        times = [record.get("_captured_at") for record in records]
        if any(value is None for value in times) or times != sorted(times) or len(times) != len(set(times)):
            errors.append("Visual iteration screenshots must be captured in strict chronological order")
        for first, second in zip(records, records[1:]):
            ratio = pixel_change_ratio(first["_decoded"], second["_decoded"])
            if ratio < 0.002:
                errors.append(
                    f"Visual iteration screenshots are only {ratio:.4%} different; declared changes need visible evidence"
                )
    missing = findings - resolved
    unknown = resolved - findings
    if missing:
        errors.append(f"Iteration findings are not linked to a resolving change: {sorted(missing)}")
    if unknown:
        errors.append(f"Iteration changes resolve unknown finding ids: {sorted(unknown)}")


def validate_independent_review(
    data: dict[str, Any],
    base_dir: Path,
    source_fingerprint: str | None,
    captures: dict[Path, dict[str, Any]],
    errors: list[str],
) -> None:
    review_path = get_path(data, "visual_review.independent_review.review_artifact")
    review, _ = load_json_file(
        review_path, base_dir, "visual_review.independent_review.review_artifact", errors
    )
    if review is None:
        return
    require_manifest_header(review, REVIEW_GENERATOR, "independent_review", errors)
    if review.get("reviewer_type") != "subagent":
        errors.append("Independent review must be produced by a fresh subagent")
    reviewer_id = normalized(review.get("reviewer_id"))
    implementer_id = normalized(review.get("implementer_id"))
    if len(reviewer_id) < 3 or len(implementer_id) < 3 or reviewer_id == implementer_id:
        errors.append("Independent review must record distinct reviewer_id and implementer_id")
    if normalized(get_path(data, "visual_review.independent_review.reviewer_name")) != reviewer_id:
        errors.append("Independent review raw reviewer_id must match the report reviewer_name")
    if get_path(data, "visual_review.independent_review.reviewer") != "subagent":
        errors.append("Independent review report reviewer must be 'subagent'")
    if review.get("prompt_blind") is not True or review.get("intended_verdict_disclosed") is not False:
        errors.append("Independent review prompt must be blind and must not disclose the intended verdict")
    prompt = review.get("neutral_prompt")
    if not isinstance(prompt, str) or len(prompt.strip()) < 120:
        errors.append("Independent review neutral_prompt must preserve the full blind review request")
    elif re.search(r"(?i)must\s+pass|expected\s+pass|verdict\s+should\s+be\s+pass", prompt):
        errors.append("Independent review prompt is leading")
    if source_fingerprint and review.get("source_fingerprint") != source_fingerprint:
        errors.append("Independent review source_fingerprint does not match the implementation")
    finished = parse_timestamp(review.get("finished_at"), "independent_review.finished_at", errors)
    latest_capture = max(
        (record.get("_captured_at") or 0 for record in captures.values()), default=0
    )
    if finished is not None and latest_capture and finished <= latest_capture:
        errors.append("Independent review must finish after the reviewed browser captures")
    reviewed_hashes = review.get("reviewed_capture_sha256")
    available_hashes = {record["_decoded"]["file_digest"] for record in captures.values()}
    if not isinstance(reviewed_hashes, list) or len(set(reviewed_hashes)) < 4:
        errors.append("Independent review must reference at least four distinct capture hashes")
    elif not set(reviewed_hashes).issubset(available_hashes):
        errors.append("Independent review references capture hashes outside the capture manifest")

    identity = review.get("identity_probe")
    if not isinstance(identity, dict):
        errors.append("Independent review identity_probe is required")
    else:
        if identity.get("branding_ignored") is not True or identity.get("branding_required") is not False:
            errors.append("Identity probe must ignore branding and succeed without it")
        for field in ("identified_product_type", "identified_primary_task"):
            if not isinstance(identity.get(field), str) or len(identity[field].strip()) < 20:
                errors.append(f"independent_review.identity_probe.{field} is too weak")
        signals = identity.get("non_cosmetic_signals")
        if not isinstance(signals, list) or len(signals) < 3:
            errors.append("Identity probe needs at least three non-cosmetic signals")
        if identity.get("verdict") != "pass":
            errors.append("Independent review identity_probe.verdict must be pass")

    action = review.get("action_probe")
    if not isinstance(action, dict):
        errors.append("Independent review action_probe is required")
    else:
        if normalized(action.get("trigger_label")) != normalized(get_path(data, "context.primary_cta")):
            errors.append("Independent review action trigger must match context.primary_cta")
        for field in (
            "predicted_outcome",
            "observed_feedback",
            "observed_terminal_state",
            "observed_recovery",
        ):
            if not isinstance(action.get(field), str) or len(action[field].strip()) < 20:
                errors.append(f"independent_review.action_probe.{field} is too weak")
        if action.get("verdict") != "pass":
            errors.append("Independent review action_probe.verdict must be pass")

    anti_slop = review.get("anti_slop_probe")
    if not isinstance(anti_slop, dict):
        errors.append("Independent review anti_slop_probe is required")
    else:
        for field in ("source_scan_reviewed", "runtime_style_reviewed", "screenshots_reviewed"):
            if anti_slop.get(field) is not True:
                errors.append(f"independent_review.anti_slop_probe.{field} must be true")
        if anti_slop.get("verdict") != "pass":
            errors.append("Independent review anti_slop_probe.verdict must be pass")
        violations = anti_slop.get("violations")
        if not isinstance(violations, list) or violations:
            errors.append("Independent review anti_slop violations must be an empty list")


def validate_lighthouse_provenance(
    data: dict[str, Any],
    base_dir: Path,
    errors: list[str],
    *,
    observed: dict[str, Any] | None = None,
    live_config_path: Path | None = None,
) -> None:
    report_path = get_path(data, "measurements.lighthouse.report")
    lighthouse, _ = load_json_file(report_path, base_dir, "measurements.lighthouse.report", errors)
    if lighthouse is None:
        return
    version = lighthouse.get("lighthouseVersion")
    if not isinstance(version, str) or not re.match(r"^\d+\.\d+", version):
        errors.append("Lighthouse artifact is missing lighthouseVersion")
    if not isinstance(lighthouse.get("finalUrl"), str) or not lighthouse["finalUrl"].startswith(("http://", "https://", "file://")):
        errors.append("Lighthouse artifact is missing a valid finalUrl")
    parse_timestamp(lighthouse.get("fetchTime"), "Lighthouse.fetchTime", errors)
    if not isinstance(lighthouse.get("userAgent"), str) or len(lighthouse["userAgent"]) < 10:
        errors.append("Lighthouse artifact is missing userAgent")
    for field in ("environment", "configSettings"):
        if not isinstance(lighthouse.get(field), dict) or not lighthouse[field]:
            errors.append(f"Lighthouse artifact is missing {field}")
    audits = lighthouse.get("audits")
    if not isinstance(audits, dict) or len(audits) < 100:
        errors.append("Lighthouse artifact must contain the full audits map, not a hand-written score stub")
        audits = {}
    canonical_audits = {
        "aria-allowed-attr",
        "button-name",
        "color-contrast",
        "cumulative-layout-shift",
        "document-title",
        "errors-in-console",
        "first-contentful-paint",
        "html-has-lang",
        "image-alt",
        "largest-contentful-paint",
        "link-name",
        "meta-viewport",
        "speed-index",
        "total-blocking-time",
    }
    missing_canonical = canonical_audits - set(audits)
    if missing_canonical:
        errors.append(f"Lighthouse artifact is missing canonical audits: {sorted(missing_canonical)}")
    categories = lighthouse.get("categories")
    if isinstance(categories, dict):
        for category_name in ("performance", "accessibility", "best-practices", "seo"):
            category = categories.get(category_name)
            if not isinstance(category, dict) or not isinstance(category.get("auditRefs"), list) or not category["auditRefs"]:
                errors.append(f"Lighthouse category {category_name} is missing auditRefs")
            elif any(
                not isinstance(reference, dict) or reference.get("id") not in audits
                for reference in category["auditRefs"]
            ):
                errors.append(f"Lighthouse category {category_name} references audits outside the full map")
    if not isinstance(lighthouse.get("runWarnings"), list):
        errors.append("Lighthouse artifact is missing runWarnings")
    elif lighthouse["runWarnings"]:
        errors.append("Lighthouse artifact runWarnings must be empty")
    if lighthouse.get("runtimeError"):
        errors.append("Lighthouse artifact contains a runtimeError")
    if not isinstance(lighthouse.get("timing"), dict) or not lighthouse["timing"]:
        errors.append("Lighthouse artifact is missing timing provenance")

    runner = Path(__file__).resolve().with_name("lighthouse_audit.js")
    provenance = lighthouse.get("_genscaff_provenance")
    if not isinstance(provenance, dict):
        errors.append("Lighthouse artifact is missing gate-owned runner provenance")
    else:
        if provenance.get("runner_sha256") != file_sha256(runner):
            errors.append("Lighthouse artifact runner sha256 does not match the gate-owned runner")
        if live_config_path is not None and provenance.get("config_sha256") != file_sha256(live_config_path):
            errors.append("Lighthouse artifact config sha256 does not match live_audit_config")
        if provenance.get("audited_url") != lighthouse.get("finalUrl"):
            errors.append("Lighthouse artifact audited_url does not match finalUrl")

    if observed is None:
        errors.append("Validator-owned Lighthouse re-execution did not produce an observation")
        return
    observed_provenance = observed.get("_genscaff_provenance")
    if not isinstance(observed_provenance, dict):
        errors.append("Validator-owned Lighthouse result is missing runner provenance")
    else:
        if observed_provenance.get("runner_sha256") != file_sha256(runner):
            errors.append("Validator-owned Lighthouse runner sha256 is invalid")
        if live_config_path is not None and observed_provenance.get("config_sha256") != file_sha256(live_config_path):
            errors.append("Validator-owned Lighthouse config sha256 is invalid")
        if observed_provenance.get("audited_url") != observed.get("finalUrl"):
            errors.append("Validator-owned Lighthouse audited_url does not match finalUrl")
    observed_audits = observed.get("audits")
    if not isinstance(observed_audits, dict) or len(observed_audits) < 100 or canonical_audits - set(observed_audits):
        errors.append("Validator-owned Lighthouse result is not a complete canonical LHR")
    thresholds = {
        "performance": 0.80,
        "accessibility": 0.95,
        "best-practices": 0.90,
        "seo": 0.90,
    }
    observed_categories = observed.get("categories")
    if not isinstance(observed_categories, dict):
        errors.append("Validator-owned Lighthouse result is missing categories")
    else:
        for category_name, threshold in thresholds.items():
            observed_category = observed_categories.get(category_name)
            observed_score = observed_category.get("score") if isinstance(observed_category, dict) else None
            if isinstance(observed_score, bool) or not isinstance(observed_score, (int, float)) or observed_score < threshold:
                errors.append(
                    f"Validator-owned Lighthouse {category_name} score must be >= {threshold:.2f}; got {observed_score!r}"
                )
                continue
            saved_category = categories.get(category_name) if isinstance(categories, dict) else None
            saved_score = saved_category.get("score") if isinstance(saved_category, dict) else None
            tolerance = 0.15 if category_name == "performance" else 0.02
            if isinstance(saved_score, (int, float)) and not isinstance(saved_score, bool) and abs(saved_score - observed_score) > tolerance:
                errors.append(
                    f"Saved and validator-owned Lighthouse {category_name} scores drift by more than {tolerance:.2f}"
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


def validate_visual_target_content(
    data: dict[str, Any], base_dir: Path, captures: dict[Path, dict[str, Any]], errors: list[str]
) -> None:
    target = resolve_path(get_path(data, "visual_target.artifact"), base_dir, "visual_target.artifact", errors)
    if target is None or not target.is_file():
        return
    try:
        text = target.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"Visual target must be readable UTF-8 text: {exc}")
        return
    words = re.findall(r"[\w가-힣]+", text.casefold(), flags=re.UNICODE)
    if len(text.encode("utf-8")) < 400 or len(words) < 70 or len(set(words)) < 30:
        errors.append("Visual target artifact is too repetitive or content-thin to constrain implementation")
    target_tokens = set(words)
    contract_tokens = meaningful_tokens(get_path(data, "context.product_type"))
    contract_tokens.update(meaningful_tokens(get_path(data, "context.primary_task")))
    if len(target_tokens & contract_tokens) < min(3, len(contract_tokens)):
        errors.append("Visual target artifact does not contain enough product-contract vocabulary")
    created_at = parse_timestamp(get_path(data, "visual_target.created_at"), "visual_target.created_at", errors)
    capture_times = [record.get("_captured_at") for record in captures.values() if record.get("_captured_at")]
    if created_at is not None and capture_times and created_at >= min(capture_times):
        errors.append("visual_target.created_at must strictly predate every browser capture")
    if created_at is not None and abs(target.stat().st_mtime - created_at) > 300:
        errors.append("visual_target.created_at must be within five minutes of the artifact mtime")


def internal_artifact_paths(data: dict[str, Any], report_path: Path) -> set[Path]:
    """Return gate-owned evidence files that must not make the source hash self-referential."""
    base_dir = report_path.resolve().parent
    values: list[Any] = [
        str(report_path.resolve()),
        get_path(data, "implementation_audit.live_audit_config"),
        get_path(data, "implementation_audit.capture_manifest"),
        get_path(data, "implementation_audit.content_manifest"),
        get_path(data, "visual_review.independent_review.review_artifact"),
        get_path(data, "measurements.lighthouse.report"),
        get_path(data, "measurements.execution_manifest"),
    ]
    for path in (
        "implementation_audit.runtime_style_manifests",
        "implementation_audit.control_manifests",
    ):
        candidates = get_path(data, path, [])
        if isinstance(candidates, list):
            values.extend(candidates)
    resolved: set[Path] = set()
    for value in values:
        if not isinstance(value, str) or not value.strip() or value.startswith(("http://", "https://")):
            continue
        candidate = Path(value).expanduser()
        if not candidate.is_absolute():
            candidate = base_dir / candidate
        try:
            resolved.add(candidate.resolve())
        except OSError:
            continue

    config_path_value = get_path(data, "implementation_audit.live_audit_config")
    if isinstance(config_path_value, str) and config_path_value.strip():
        config_path = Path(config_path_value).expanduser()
        if not config_path.is_absolute():
            config_path = base_dir / config_path
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
            output_value = config.get("output_dir") if isinstance(config, dict) else None
            if isinstance(output_value, str) and output_value.strip():
                output_dir = Path(output_value).expanduser()
                if not output_dir.is_absolute():
                    output_dir = config_path.resolve().parent / output_dir
                resolved.add((output_dir / "live-audit-bundle.json").resolve())
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            pass
    return resolved


def validate(
    data: dict[str, Any],
    report_path: Path,
    *,
    _live_bundle_override: dict[str, Any] | None = None,
    _lighthouse_bundle_override: dict[str, Any] | None = None,
    execute_approved_commands: bool = False,
) -> list[str]:
    errors: list[str] = []
    base_dir = report_path.resolve().parent
    _, source_fingerprint = validate_source_audit(
        data,
        base_dir,
        errors,
        excluded_artifacts=internal_artifact_paths(data, report_path),
    )
    live_bundle, live_config, live_config_path = run_live_audit(
        data,
        base_dir,
        source_fingerprint,
        errors,
        bundle_override=_live_bundle_override,
    )
    lighthouse_bundle = run_lighthouse_audit(
        live_config_path,
        errors,
        bundle_override=_lighthouse_bundle_override,
    )
    captures, _ = validate_capture_manifest(data, base_dir, source_fingerprint, errors)
    validate_live_audit_bundle(
        live_bundle,
        live_config,
        live_config_path,
        data,
        base_dir,
        source_fingerprint,
        captures,
        errors,
    )
    validate_style_manifests(data, base_dir, source_fingerprint, errors)
    validate_control_manifests(data, base_dir, source_fingerprint, errors)
    validate_content_manifest(data, base_dir, source_fingerprint, captures, errors)
    validate_action_and_state_evidence(data, base_dir, captures, errors)
    validate_substitution(data, errors)
    validate_iteration_evidence(data, base_dir, captures, errors)
    validate_independent_review(data, base_dir, source_fingerprint, captures, errors)
    validate_lighthouse_provenance(
        data,
        base_dir,
        errors,
        observed=lighthouse_bundle,
        live_config_path=live_config_path,
    )
    validate_execution_manifest(
        data,
        base_dir,
        source_fingerprint,
        errors,
        execute_approved_commands=execute_approved_commands,
    )
    validate_visual_target_content(data, base_dir, captures, errors)
    return errors
