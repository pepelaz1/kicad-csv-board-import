"""Parse a small, explicit CSV geometry format independent of KiCad."""

import csv
import math
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Primitive:
    kind: str
    layer: str
    start: tuple[float, float]
    end: tuple[float, float] | None = None
    center: tuple[float, float] | None = None
    direction: str = ""
    width: float = 0.0
    radius: float = 0.0
    middle: tuple[float, float] | None = None


def _number(row, key, line):
    try:
        value = float(row[key])
    except (KeyError, ValueError, TypeError):
        raise ValueError(f"CSV row {line}: {key} must be a number") from None
    if not math.isfinite(value):
        raise ValueError(f"CSV row {line}: {key} must be finite")
    return value


def _point(row, prefix, line):
    return (_number(row, f"{prefix}_x", line), _number(row, f"{prefix}_y", line))


def arc_middle(start, end, center, direction):
    """Direction is as seen in KiCad: +X right, +Y down."""
    r1 = math.dist(start, center)
    r2 = math.dist(end, center)
    if r1 < 0.01 or math.dist(start, end) < 0.01:
        raise ValueError("arc radius and endpoint separation must be nonzero")
    if abs(r1 - r2) > 0.01:
        raise ValueError("arc start and end must be equidistant from center (0.01 mm tolerance)")
    a0 = math.atan2(start[1] - center[1], start[0] - center[0])
    a1 = math.atan2(end[1] - center[1], end[0] - center[0])
    if direction == "CW":
        sweep = (a1 - a0) % (2 * math.pi)
        angle = a0 + sweep / 2
    elif direction == "CCW":
        sweep = (a0 - a1) % (2 * math.pi)
        angle = a0 - sweep / 2
    else:
        raise ValueError("arc direction must be CW or CCW")
    return (center[0] + r1 * math.cos(angle), center[1] + r1 * math.sin(angle))


def read_primitives(path: Path):
    items = []
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        expected = {"kind", "layer", "start_x", "start_y", "end_x", "end_y",
                    "center_x", "center_y", "direction", "width", "radius"}
        if not reader.fieldnames or not expected.issubset(reader.fieldnames):
            raise ValueError("CSV header must contain: " + ", ".join(sorted(expected)))
        for line, row in enumerate(reader, 2):
            kind = (row["kind"] or "").strip().lower()
            start = _point(row, "start", line)
            if any(v < 0 for v in start):
                raise ValueError(f"CSV row {line}: coordinates must be nonnegative")
            if kind == "hole":
                radius = _number(row, "radius", line)
                if radius <= 0:
                    raise ValueError(f"CSV row {line}: radius must be positive")
                items.append(Primitive(kind, "", start, radius=radius))
                continue
            if kind not in {"line", "arc"}:
                raise ValueError(f"CSV row {line}: kind must be line, arc or hole")
            layer = (row["layer"] or "").strip()
            if layer not in {"F.Cu", "B.Cu"}:
                raise ValueError(f"CSV row {line}: only F.Cu and B.Cu are supported")
            end = _point(row, "end", line)
            if any(v < 0 for v in end) or end == start:
                raise ValueError(f"CSV row {line}: invalid endpoint")
            width = _number(row, "width", line)
            if width <= 0:
                raise ValueError(f"CSV row {line}: width must be positive")
            if kind == "arc":
                center = _point(row, "center", line)
                direction = (row["direction"] or "").strip().upper()
                try:
                    middle = arc_middle(start, end, center, direction)
                except ValueError as exc:
                    raise ValueError(f"CSV row {line}: {exc}") from exc
                items.append(Primitive(kind, layer, start, end, center, direction, width, middle=middle))
            else:
                items.append(Primitive(kind, layer, start, end, width=width))
    if not items:
        raise ValueError("CSV has no geometry rows")
    return items
