"""Strict manifest constants, shared text helpers, and audit caches."""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any


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


def require_manifest_header(
    manifest: dict[str, Any], generator: str, path: str, errors: list[str]
) -> None:
    if manifest.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        errors.append(f"{path}.schema_version must be {MANIFEST_SCHEMA_VERSION}")
    if manifest.get("generated_by") != generator:
        errors.append(f"{path}.generated_by must be {generator!r}")
