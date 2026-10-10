"""Session 168, part D: the price board's placeholder where the workbench opens.

The owner's instruction of 8 October 2026: before any row is clicked, the workbench's place shows a quiet empty panel of
the same size and position (docked on the right on wide screens, above the tables on narrow ones), the faint outline of
a chart, and one small line; a click replaces it with the workbench, exactly as before. The box was measured in a real
browser at three widths (runs/session168/measure-board.mjs); here, the file's contents.
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class Placeholder(unittest.TestCase):
    def test_the_placeholder_takes_the_workbenchs_box(self):
        v = src("site", "components", "board", "BoardView.tsx")
        self.assertIn('const BENCH_ASIDE = "min-w-0 max-xl:order-first xl:sticky xl:top-2 xl:max-h-[calc(100vh-1rem)] xl:self-start xl:overflow-y-auto";', v)
        self.assertIn('const BENCH_GRID = "grid gap-4 xl:grid-cols-[minmax(0,1fr)_minmax(460px,42%)]";', v)
        self.assertEqual(v.count("<aside className={BENCH_ASIDE}"), 2)          # the workbench and the placeholder, one box
        self.assertIn("<div className={!openRow || !bench.x ? BENCH_GRID : \"\"}>", v)

    def test_an_outline_drawn_and_one_line(self):
        v = src("site", "components", "board", "BoardView.tsx")
        block = v.split("function BenchPlaceholder()", 1)[1].split("\n}\n", 1)[0]
        self.assertIn("Click any row to open the markets workbench here.", block)
        self.assertIn("<svg", block)
        self.assertEqual(block.count("<line "), 3)                                  # three light grid lines
        self.assertIn("<polyline", block)                                           # the two axes
        self.assertNotIn("<img", block)
        self.assertNotIn("url(", block)

    def test_no_em_dash(self):
        for parts in (("site", "components", "board", "BoardView.tsx"), ("tests", "test_session168_board.py")):
            self.assertNotIn(chr(0x2014), src(*parts), parts[-1])


if __name__ == "__main__":
    unittest.main()
