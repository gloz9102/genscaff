"""Inspect local report artifacts and evidence references."""
from __future__ import annotations

import hashlib
import struct
from pathlib import Path
from typing import Any
from .report_constants import (
    IMAGE_SUFFIXES,
    MIN_IMAGE_BYTES,
    MIN_IMAGE_HEIGHT,
    MIN_IMAGE_WIDTH,
)
from .report_fields import (
    require_list_value,
    require_text_value,
)


class ArtifactInspector:
    def __init__(self, report_path: Path, evidence_catalog: dict[str, Any] | None = None):
        self.base_dir = report_path.resolve().parent
        self.file_cache: dict[Path, tuple[int, str]] = {}
        self.image_cache: dict[Path, tuple[int, int, str]] = {}
        self.evidence_catalog = evidence_catalog or {}

    def resolve(self, value: str) -> Path:
        candidate = Path(value).expanduser()
        if not candidate.is_absolute():
            candidate = self.base_dir / candidate
        return candidate.resolve()

    def inspect_file(
        self,
        value: Any,
        path: str,
        errors: list[str],
        *,
        allowed_suffixes: set[str] | None = None,
        minimum_bytes: int = 1,
    ) -> Path | None:
        text = require_text_value(value, path, errors, minimum=3)
        if text is None:
            return None
        if text.startswith(("http://", "https://")):
            errors.append(f"Remote artifact is not independently verifiable: {path}")
            return None
        candidate = self.resolve(text)
        if not candidate.is_file():
            errors.append(f"Artifact does not exist or is not a file: {path} -> {candidate}")
            return None
        if allowed_suffixes and candidate.suffix.casefold() not in allowed_suffixes:
            errors.append(
                f"Artifact has unsupported extension at {path}: {candidate.suffix or '<none>'}"
            )
            return None
        size = candidate.stat().st_size
        if size < minimum_bytes:
            errors.append(f"Artifact is too small at {path}: {size} bytes")
            return None
        if candidate not in self.file_cache:
            digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
            self.file_cache[candidate] = (size, digest)
        return candidate

    def inspect_image(self, value: Any, path: str, errors: list[str]) -> Path | None:
        candidate = self.inspect_file(
            value,
            path,
            errors,
            allowed_suffixes=IMAGE_SUFFIXES,
            minimum_bytes=MIN_IMAGE_BYTES,
        )
        if candidate is None:
            return None
        if candidate not in self.image_cache:
            dimensions = image_dimensions(candidate)
            if dimensions is None:
                errors.append(f"Artifact is not a supported image: {path} -> {candidate}")
                return None
            width, height = dimensions
            digest = self.file_cache[candidate][1]
            self.image_cache[candidate] = (width, height, digest)
        width, height, _ = self.image_cache[candidate]
        if width < MIN_IMAGE_WIDTH or height < MIN_IMAGE_HEIGHT:
            errors.append(
                f"Image dimensions are too small at {path}: {width}x{height}; "
                f"minimum {MIN_IMAGE_WIDTH}x{MIN_IMAGE_HEIGHT}"
            )
        return candidate

    def image_digest(self, candidate: Path) -> str:
        return self.image_cache[candidate][2]


def image_dimensions(path: Path) -> tuple[int, int] | None:
    with path.open("rb") as stream:
        header = stream.read(24)
        if header.startswith(b"\x89PNG\r\n\x1a\n") and len(header) >= 24:
            return struct.unpack(">II", header[16:24])
        if header[:6] in (b"GIF87a", b"GIF89a") and len(header) >= 10:
            return struct.unpack("<HH", header[6:10])
        if header[:2] != b"\xff\xd8":
            return None

        stream.seek(2)
        while True:
            byte = stream.read(1)
            if not byte:
                return None
            if byte != b"\xff":
                continue
            marker = stream.read(1)
            while marker == b"\xff":
                marker = stream.read(1)
            if not marker:
                return None
            marker_value = marker[0]
            if marker_value in {0xD8, 0xD9}:
                continue
            length_bytes = stream.read(2)
            if len(length_bytes) != 2:
                return None
            segment_length = struct.unpack(">H", length_bytes)[0]
            if segment_length < 2:
                return None
            if marker_value in {
                0xC0,
                0xC1,
                0xC2,
                0xC3,
                0xC5,
                0xC6,
                0xC7,
                0xC9,
                0xCA,
                0xCB,
                0xCD,
                0xCE,
                0xCF,
            }:
                payload = stream.read(5)
                if len(payload) != 5:
                    return None
                height, width = struct.unpack(">HH", payload[1:5])
                return width, height
            stream.seek(segment_length - 2, 1)


def validate_inline_evidence(
    value: Any,
    path: str,
    inspector: ArtifactInspector,
    errors: list[str],
) -> None:
    if not isinstance(value, dict):
        errors.append(f"Evidence must be an object: {path}")
        return
    inspector.inspect_image(value.get("artifact"), f"{path}.artifact", errors)
    require_text_value(value.get("region"), f"{path}.region", errors, minimum=12)
    require_text_value(value.get("observation"), f"{path}.observation", errors, minimum=30)


def validate_evidence_catalog(
    value: Any,
    inspector: ArtifactInspector,
    errors: list[str],
) -> None:
    if value is None:
        return
    if not isinstance(value, dict):
        errors.append("evidence_catalog must be an object when provided")
        return
    for evidence_id, item in value.items():
        require_text_value(evidence_id, f"evidence_catalog key {evidence_id!r}", errors, minimum=3)
        validate_inline_evidence(item, f"evidence_catalog.{evidence_id}", inspector, errors)


def validate_evidence(
    value: Any,
    path: str,
    inspector: ArtifactInspector,
    errors: list[str],
) -> None:
    if isinstance(value, str):
        evidence_id = require_text_value(value, path, errors, minimum=3)
        if evidence_id is not None and evidence_id not in inspector.evidence_catalog:
            errors.append(f"Unknown evidence reference at {path}: {evidence_id!r}")
        return
    validate_inline_evidence(value, path, inspector, errors)


def validate_evidence_list(
    value: Any,
    path: str,
    inspector: ArtifactInspector,
    errors: list[str],
    *,
    minimum: int = 1,
) -> None:
    items = require_list_value(value, path, errors, minimum=minimum)
    if items is None:
        return
    for index, item in enumerate(items):
        validate_evidence(item, f"{path}[{index}]", inspector, errors)
