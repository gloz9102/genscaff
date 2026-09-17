"""Typed report field checks and placeholder detection."""
from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any
from .report_constants import (
    PLACEHOLDER_MARKERS,
    TRIVIAL_TEXT,
)


def get_path(data: dict[str, Any], path: str) -> Any:
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            raise KeyError(path)
        current = current[part]
    return current


def normalized_text(value: str) -> str:
    return " ".join(value.casefold().split())


def parse_timestamp(value: str, path: str, errors: list[str]) -> float | None:
    normalized = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        errors.append(f"{path} must be a valid ISO-8601 timestamp with timezone")
        return None
    if parsed.tzinfo is None:
        errors.append(f"{path} must include a timezone")
        return None
    return parsed.astimezone(timezone.utc).timestamp()


def placeholder_reason(value: str) -> str | None:
    normalized = normalized_text(value)
    if normalized in TRIVIAL_TEXT:
        return "trivial self-attestation"
    for marker in PLACEHOLDER_MARKERS:
        if marker in normalized:
            return f"placeholder marker '{marker}'"
    return None


def require_text_value(
    value: Any,
    path: str,
    errors: list[str],
    *,
    minimum: int = 1,
    allow_placeholder: bool = False,
) -> str | None:
    if not isinstance(value, str):
        errors.append(f"Required text is not a string: {path}")
        return None
    stripped = value.strip()
    if len(stripped) < minimum:
        errors.append(f"Required text is too short: {path} (minimum {minimum} characters)")
        return None
    if not allow_placeholder:
        reason = placeholder_reason(stripped)
        if reason:
            errors.append(f"Invalid evidence text at {path}: {reason}")
            return None
    return stripped


def require_text(
    data: dict[str, Any], path: str, errors: list[str], *, minimum: int = 1
) -> str | None:
    try:
        value = get_path(data, path)
    except KeyError:
        errors.append(f"Missing required text: {path}")
        return None
    return require_text_value(value, path, errors, minimum=minimum)


def require_bool(data: dict[str, Any], path: str, errors: list[str], expected: bool = True) -> None:
    try:
        value = get_path(data, path)
    except KeyError:
        errors.append(f"Missing required boolean: {path}")
        return
    if value is not expected:
        errors.append(f"Required boolean must be {str(expected).lower()}: {path}")


def require_number(
    data: dict[str, Any],
    path: str,
    errors: list[str],
    *,
    minimum: float | None = None,
    maximum: float | None = None,
    integer: bool = False,
) -> float | int | None:
    try:
        value = get_path(data, path)
    except KeyError:
        errors.append(f"Missing required number: {path}")
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        errors.append(f"Required number is not numeric: {path}")
        return None
    if not math.isfinite(float(value)):
        errors.append(f"Required number is not finite: {path}")
        return None
    if integer and not isinstance(value, int):
        errors.append(f"Required number must be an integer: {path}")
    if minimum is not None and value < minimum:
        errors.append(f"{path} must be >= {minimum}; got {value}")
    if maximum is not None and value > maximum:
        errors.append(f"{path} must be <= {maximum}; got {value}")
    return value


def require_enum(
    data: dict[str, Any], path: str, allowed: set[str], errors: list[str]
) -> str | None:
    try:
        value = get_path(data, path)
    except KeyError:
        errors.append(f"Missing required enum: {path}")
        return None
    if not isinstance(value, str) or value not in allowed:
        choices = ", ".join(sorted(allowed))
        errors.append(f"{path} must be one of [{choices}]; got {value!r}")
        return None
    return value


def require_list_value(value: Any, path: str, errors: list[str], *, minimum: int = 0) -> list[Any] | None:
    if not isinstance(value, list):
        errors.append(f"Required list is missing or invalid: {path}")
        return None
    if len(value) < minimum:
        errors.append(f"{path} must contain at least {minimum} item(s); got {len(value)}")
    return value


def require_list(data: dict[str, Any], path: str, errors: list[str], *, minimum: int = 0) -> list[Any] | None:
    try:
        value = get_path(data, path)
    except KeyError:
        errors.append(f"Missing required list: {path}")
        return None
    return require_list_value(value, path, errors, minimum=minimum)


def validate_text_list(
    value: Any,
    path: str,
    errors: list[str],
    *,
    minimum_items: int,
    minimum_length: int,
) -> list[str]:
    items = require_list_value(value, path, errors, minimum=minimum_items)
    if items is None:
        return []
    valid: list[str] = []
    for index, item in enumerate(items):
        text = require_text_value(item, f"{path}[{index}]", errors, minimum=minimum_length)
        if text is not None:
            valid.append(text)
    normalized = [normalized_text(item) for item in valid]
    if len(normalized) != len(set(normalized)):
        errors.append(f"{path} must contain unique items")
    return valid


def require_empty_list(data: dict[str, Any], path: str, errors: list[str]) -> None:
    items = require_list(data, path, errors)
    if items is not None and items:
        errors.append(f"{path} must be empty for PASS; got {len(items)} item(s)")


def get_path_or_none(data: dict[str, Any], path: str) -> Any:
    try:
        return get_path(data, path)
    except KeyError:
        return None
