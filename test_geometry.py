import math
import unittest
from pathlib import Path

from geometry import arc_middle, read_primitives


class GeometryTests(unittest.TestCase):
    def test_sample_contains_line_arc_and_holes(self):
        items = read_primitives(Path(__file__).with_name("sample.csv"))
        self.assertEqual([item.kind for item in items],
                         ["line", "line", "arc", "line", "hole", "hole"])
        self.assertEqual(items[2].middle[0], items[2].middle[1])

    def test_semicircle_direction_changes_side(self):
        start, end, center = (10, 20), (30, 20), (20, 20)
        cw = arc_middle(start, end, center, "CW")
        ccw = arc_middle(start, end, center, "CCW")
        self.assertAlmostEqual(cw[1], 10)
        self.assertAlmostEqual(ccw[1], 30)

    def test_rejects_nonconcentric_endpoints(self):
        with self.assertRaisesRegex(ValueError, "equidistant"):
            arc_middle((10, 10), (25, 20), (20, 20), "CW")


if __name__ == "__main__":
    unittest.main()
