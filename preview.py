"""Render a visual CSV preview without requiring KiCad."""

import argparse
import html
import math
from pathlib import Path

from geometry import read_primitives


def render(items):
    points = [p for item in items for p in (item.start, item.end, item.middle) if p]
    max_x = max(p[0] for p in points) + 8
    max_y = max(p[1] for p in points) + 8
    paths = []
    for item in items:
        if item.kind == "hole":
            paths.append(f'<circle cx="{item.start[0]}" cy="{item.start[1]}" r="{item.radius}" fill="#f8fafc" stroke="#f59e0b" stroke-width="0.2"/>')
        elif item.kind == "line":
            paths.append(f'<path d="M {item.start[0]} {item.start[1]} L {item.end[0]} {item.end[1]}" stroke="#00a87e" stroke-width="{item.width}" fill="none" stroke-linecap="round"/>')
        else:
            r = math.dist(item.start, item.center)
            a0 = math.atan2(item.start[1]-item.center[1], item.start[0]-item.center[0])
            a1 = math.atan2(item.end[1]-item.center[1], item.end[0]-item.center[0])
            sweep = ((a1-a0) if item.direction == "CW" else (a0-a1)) % (2*math.pi)
            large = 1 if sweep > math.pi else 0
            sweep_flag = 1 if item.direction == "CW" else 0
            paths.append(f'<path d="M {item.start[0]} {item.start[1]} A {r} {r} 0 {large} {sweep_flag} {item.end[0]} {item.end[1]}" stroke="#00a87e" stroke-width="{item.width}" fill="none" stroke-linecap="round"/>')
    legend = f"{len(items)} CSV objects · mm · green = copper, orange = NPTH holes"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {max_x} {max_y}" width="1000" height="760">'
            f'<rect width="100%" height="100%" fill="#f8fafc"/>'
            f'<g>{"".join(paths)}</g>'
            f'<text x="1" y="{max_y-1}" font-family="Arial" font-size="0.7" fill="#334155">{html.escape(legend)}</text>'
            '</svg>')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path)
    parser.add_argument("svg", type=Path)
    args = parser.parse_args()
    args.svg.parent.mkdir(parents=True, exist_ok=True)
    args.svg.write_text(render(read_primitives(args.csv)), encoding="utf-8")
    print(f"Created {args.svg}")


if __name__ == "__main__":
    main()
