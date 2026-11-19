"""Create a KiCad board from validated CSV using KiCad's pcbnew Python module."""

import argparse
import sys
from pathlib import Path

from geometry import read_primitives


def create_board(items, output):
    try:
        import pcbnew as pcb
    except ImportError as exc:
        raise RuntimeError(
            "KiCad pcbnew is unavailable. Run this with the Python supplied by KiCad, "
            "or add its scripting module to PYTHONPATH."
        ) from exc

    board = pcb.BOARD()
    layers = {"F.Cu": pcb.F_Cu, "B.Cu": pcb.B_Cu}
    point = lambda p: pcb.VECTOR2I(pcb.FromMM(p[0]), pcb.FromMM(p[1]))
    hole_number = 0
    for item in items:
        if item.kind == "line":
            shape = pcb.PCB_TRACK(board)
            shape.SetStart(point(item.start))
            shape.SetEnd(point(item.end))
            shape.SetWidth(pcb.FromMM(item.width))
            shape.SetLayer(layers[item.layer])
            board.Add(shape)
        elif item.kind == "arc":
            shape = pcb.PCB_ARC(board)
            shape.SetStart(point(item.start))
            shape.SetMid(point(item.middle))
            shape.SetEnd(point(item.end))
            shape.SetWidth(pcb.FromMM(item.width))
            shape.SetLayer(layers[item.layer])
            board.Add(shape)
        else:
            # A circle means a non-plated mechanical hole, not a copper via.
            hole_number += 1
            footprint = pcb.FOOTPRINT(board)
            footprint.SetReference(f"H{hole_number}")
            footprint.SetValue("NPTH")
            footprint.SetPosition(point(item.start))
            pad = pcb.PAD(footprint)
            pad.SetAttribute(pcb.PAD_ATTRIB_NPTH)
            pad.SetShape(pcb.PAD_SHAPE_CIRCLE)
            diameter = item.radius * 2
            pad.SetSize(point((diameter, diameter)))
            pad.SetDrillSize(point((diameter, diameter)))
            pad.SetPosition(point(item.start))
            footprint.Add(pad)
            board.Add(footprint)
    output.parent.mkdir(parents=True, exist_ok=True)
    pcb.SaveBoard(str(output), board)
    return board


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path)
    parser.add_argument("board", type=Path)
    args = parser.parse_args()
    try:
        items = read_primitives(args.csv)
        create_board(items, args.board)
    except (ValueError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(f"Created {args.board}: {len(items)} geometry rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
