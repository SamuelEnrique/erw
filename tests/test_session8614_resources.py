"""Session 8614 (chain 504, 19 November 2026): the resource map's record at rest follows the frame it describes.

Energy Research Warehouse (ERW). The map writes what it has drawn (data-drawn on the map's box, data-level on a
layer's row) when the view comes to rest, by a timer of 160 ms; the frame is drawn by requestAnimationFrame. Where the
frame came later than the timer, the record was written first and stayed wrong until the map next moved: the browser
check read "0 cells in view", or the coarser level, with the layer on the canvas (one run in three on this laptop, two
layers on production). The rest now draws a frame that is asked for and not yet drawn before it writes the record.
The browser check holds every frame back 400 ms and reads the record (site/scripts/check-resources.mjs). Nothing here
sets the environment or makes a request.
"""

import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EM = chr(0x2014)


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheRecordAtRest(unittest.TestCase):
    def setUp(self):
        self.m = src("site", "app", "resources", "ResourceMap.tsx")
        a = self.m.index("const settle = useCallback(() => {")
        self.settle = self.m[a:self.m.index("const moved = useCallback(", a)]

    def test_a_pending_frame_is_drawn_before_the_record_is_written(self):
        s = self.settle
        self.assertIn("const pending = raf.current !== 0;", s)
        self.assertIn("if (pending) { cancelAnimationFrame(raf.current); raf.current = 0; }", s)
        self.assertIn("if (L.moving) { L.moving = false; draw(); } else if (pending) draw();", s)
        self.assertLess(s.index("else if (pending) draw();"), s.index("el.dataset.drawn = JSON.stringify(S.drawn);"))
        self.assertLess(s.index("else if (pending) draw();"), s.index("setLevels("))

    def test_one_frame_and_no_more(self):
        # a frame at rest is drawn once: the pending one is cancelled before the rest's own
        s = self.settle
        self.assertLess(s.index("cancelAnimationFrame(raf.current)"), s.index("L.moving = false; draw();"))
        import re
        self.assertEqual(len(re.findall(r"(?<![A-Za-z])draw\(\);", s)), 2)   # the two arms of one choice ("redraw();" is another thing)

    def test_the_rest_is_still_a_timer_of_160_ms(self):
        self.assertIn("}, 160);", self.settle)


class TheCheck(unittest.TestCase):
    def test_frames_are_held_back_longer_than_the_rest(self):
        s = src("site", "scripts", "check-resources.mjs")
        self.assertIn("window.requestAnimationFrame = (f) =>", s)
        self.assertIn("}, 400)); return k; };", s)
        self.assertIn("with every frame held back 400 ms, the record at rest still names", s)

    def test_no_em_dash(self):
        for p in (("site", "app", "resources", "ResourceMap.tsx"), ("site", "scripts", "check-resources.mjs"), ("tests", "test_session8614_resources.py")):
            self.assertNotIn(EM, src(*p), p)


if __name__ == "__main__":
    unittest.main()
