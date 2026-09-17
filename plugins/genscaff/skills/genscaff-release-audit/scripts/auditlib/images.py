"""Decode PNG evidence and measure capture structure and change."""
from __future__ import annotations

import hashlib
import struct
import zlib
from pathlib import Path
from typing import Any
from .hard_common import (
    BROWSER_IMAGE_SUFFIXES,
    MAX_IMAGE_PIXELS,
    PNG_DECODE_CACHE,
)


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
